"""python -m streamlit run dashboard/app.py"""
import json
import os
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
from property_research.comparables import select_comparables

st.set_page_config(page_title="Property Market Research",layout="wide")
root=Path(__file__).resolve().parents[1]
out=Path(os.environ.get("PROPERTY_OUTPUT_DIR",str(root/"outputs")))
st.title("Brooklyn Multifamily Market Research")
st.caption("NYC Department of Finance · public recorded sales · classes C1, C2 and C3")
if not (out/"manifest.json").exists():
    st.info("Run python -m property_research.pipeline --snapshot from the project root.")
    st.stop()
m=json.loads((out/"manifest.json").read_text())
st.warning("Appraisal-support research only. No certified appraisal or opinion of market value. Transactions and property attributes need appraiser verification.")
st.caption("Historical sale-date cutoff: "+m["cutoff"]+". Later-published source files are used; this is not a point-in-time historical appraisal.")
@st.cache_data
def load(path,stamp):return pd.read_csv(path)
def read(name):
    p=out/name
    return load(str(p),p.stat().st_mtime_ns)
tabs=st.tabs(["Market overview","Comparable screening","Data quality & sources","Appraisal-support report"])
with tabs[0]:
    cols=st.columns(3)
    for col,label,key in zip(cols,["Source scope records","Research-eligible sales","Flagged / excluded"],["scope_rows","eligible_rows","excluded_rows"]):
        col.metric(label,f"{m[key]:,}")
    trend=read("quarterly_trends.csv")
    st.plotly_chart(px.line(trend,x="quarter",y="median_ppsf",color="building_class_at_time_of_sale",markers=True),width="stretch")
    st.caption("Median recorded price / gross square foot. Quarterly changes can reflect property mix; they are not a repeat-sales appreciation index.")
    markets=read("neighborhood_summary.csv")
    cls=st.selectbox("Building class",["All"]+sorted(markets.building_class_at_time_of_sale.unique().tolist()))
    if cls!="All":markets=markets[markets.building_class_at_time_of_sale==cls]
    st.dataframe(markets,hide_index=True)
with tabs[1]:
    sales=read("screened_sales.csv")
    eligible=sales[sales.eligible].copy()
    options=eligible.record_id.tolist()
    labels=eligible.set_index("record_id").address.to_dict()
    default=options.index(m["subject"]["record_id"]) if m["subject"].get("record_id") in options else 0
    selected_id=st.selectbox("Example subject profile",options,index=default,format_func=lambda x:labels[x]+" · "+x)
    row=eligible[eligible.record_id==selected_id].iloc[0]
    subject={k:row[k] for k in ["bbl","neighborhood","building_class_at_time_of_sale","gross_square_feet","year_built","residential_units"]}
    st.write(f"{row.address} · {row.neighborhood} · {row.building_class_at_time_of_sale} · {row.gross_square_feet:,.0f} gross SF")
    st.caption("The subject's recorded price is not used to rank comparables; every transfer of its parcel is excluded.")
    selected,audit,summary=select_comparables(sales,subject,m["config"])
    st.info(f"{summary['status']} · {summary['count']} selected comparables")
    st.dataframe(selected[["rank","address","sale_date","sale_price","gross_square_feet","price_per_sqft","similarity_score","source_id","source_row"]],hide_index=True)
    st.download_button("Download comparable evidence",selected.to_csv(index=False),"comparable_sales.csv","text/csv")
    with st.expander("Candidate exclusions and ranking audit"):
        st.dataframe(audit[["record_id","address","candidate_exclusions","selection_status"]],hide_index=True)
with tabs[2]:
    st.dataframe(read("quality_reconciliation.csv"),hide_index=True)
    st.caption("Primary reasons add to the input count. review_exclusions.csv retains all overlapping flags. Screens do not verify arm's-length status.")
    st.dataframe(read("review_exclusions.csv").head(500),hide_index=True)
    st.markdown("[NYC DOF annual sales source](https://www.nyc.gov/site/finance/property/property-annualized-sales-update.page)")
    st.json(m["sources"])
with tabs[3]:
    text=(out/"appraisal_support_report.md").read_text()
    st.markdown(text)
    st.download_button("Download research report",text,"appraisal_support_report.md","text/markdown")
    st.dataframe(read("review_checklist.csv"),hide_index=True)
