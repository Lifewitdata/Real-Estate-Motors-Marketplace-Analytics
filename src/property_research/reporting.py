"""Actual data reports; asking prices and concluded appraisal values are not invented."""
from html import escape
import pandas as pd
import plotly.express as px

LIMITS="""This packet supports research under an appraiser's supervision. It is not a certified appraisal or an opinion of market value. Recorded consideration is not verified arm's-length consideration. No transaction terms, financing, condition, inspection, rent roll, NOI, lease terms, occupancy, cap rate, zoning verification or professional adjustments are available. No income or cost approach is fabricated. Neighborhood matches are administrative geography, not a verified distance radius. Area and unit figures require verification. Later-released 2024/2025 workbooks supply historical sale records and roll-based attributes; this is not a point-in-time reconstruction of information available at the stated sale-date cutoff. Changing quarterly medians can reflect the composition of properties sold, not appreciation of a fixed property."""

def write_reports(out,m,comps):
    s=m["subject"];summary=m["comparables"]
    fmt=lambda x:"Not reported" if x is None else f"${x:,.2f}"
    columns=["rank","record_id","address","bbl","sale_date","sale_price","gross_square_feet","price_per_sqft","residential_units","year_built","similarity_score","source_id","source_row"]
    records=comps[columns].copy()
    table=records.to_csv(index=False)
    records.to_csv(out/"appraiser_comparable_schedule.csv",index=False)
    brief=f"""# Real Estate Market Research & Comparable Sales

## Assignment and scope
Educational acquisition/disposition research-support scenario: Brooklyn walk-up apartment buildings, classes C1, C2 and C3. Sale-date cutoff: **{m['cutoff']}**. No actual client, inspection, appraiser review or lending decision is claimed.

## Data and quality
Official source extract: **{m['scope_rows']:,} records**; **{m['eligible_rows']:,} research-eligible sales**; **{m['excluded_rows']:,} flagged/excluded records**. Reasons reconcile to the input count in quality_reconciliation.csv. Screens retain a separate review file; they do not certify that retained sales are arm's length. Repeated same-date consideration across distinct parcels is held for possible package-sale review; unrelated sales may also be flagged. Detection is limited to the committed property-class scope and cannot identify every package. Third-party provenance and publisher notes are in manifest.json and docs/sources.md.

## Example subject profile
Address: **{s.get('address','User-supplied subject')}**. BBL: {s['bbl']}. Neighborhood: {s['neighborhood']}. Class: {s['building_class_at_time_of_sale']}. Gross area: {s['gross_square_feet']:,.0f} square feet. Residential units: {s['residential_units']}. Year built: {s['year_built']}.

The default profile is selected deterministically from the most represented eligible 2025 neighborhood/class group, choosing its median-sized profile. It is an illustrative recorded property, not a client assignment. Its sale price is not an input to selection and every sale of its parcel is withheld from the comparable pool.

## Comparable screening
Require the same neighborhood and exact class, a recorded sale within {m['config']['lookback_days']} days before the cutoff, gross area within {m['config']['max_size_difference']:.0%}, construction year within {m['config']['max_age_difference_years']} years, and unit count within {m['config']['max_unit_difference']}. Keep at most one recent qualifying sale per parcel. Rank eligible candidates by a documented size/age/recency/unit similarity score. No price-based ranking, undisclosed relaxation or invented adjustments are used.

**Status: {summary['status']}**. Selected comparable count: **{summary['count']}**.
Observed unadjusted comparable median: **{fmt(summary['median_ppsf'])}/gross square foot**.
Observed interquartile spread: **{fmt(summary['q25_ppsf'])}–{fmt(summary['q75_ppsf'])}/gross square foot**.
These are descriptive statistics of selected transactions, not a value range or concluded subject value. With fewer than three comparables, statistics are withheld. See appraiser_comparable_schedule.csv for the source-traceable schedule and comparable_audit.csv for each candidate's selection/exclusion rationale.

## Next actions for supervised report preparation
1. Confirm source record/deed and whether each transaction is arm's length, bundled or subject to unusual financing.
2. Verify subject and comparable area, units, condition, renovations, tenancy, zoning and property rights with authorised sources.
3. Ask the supervising appraiser whether location, condition, size or time adjustments are supportable; document evidence before applying them.
4. Obtain verified rents, expenses, leases and occupancy before considering an income approach. No implied cap rate is calculated here.
5. Record reviewer identity, date, acceptance/rejection of each comparable and unresolved evidence before any appraisal conclusion.

## Limitations
{LIMITS}
"""
    (out/"appraisal_support_report.md").write_text(brief)
    pd.DataFrame([dict(item=x,status="Pending",owner="Supervising appraiser / authorised researcher",evidence="") for x in
        ["Arm's-length/deed verification","Area and unit verification","Condition/inspection","Property rights and zoning","Rent roll and operating expenses","Comparable acceptance and adjustments","Final reviewer approval"]]).to_csv(out/"review_checklist.csv",index=False)
    monthly=pd.read_csv(out/"quarterly_trends.csv")
    neighborhood=pd.read_csv(out/"neighborhood_summary.csv")
    charts=[px.line(monthly,x="quarter",y="median_ppsf",color="building_class_at_time_of_sale",markers=True,
        title="Observed quarterly median sale price per gross square foot"),
        px.bar(neighborhood.head(15),x="median_ppsf",y="neighborhood",color="building_class_at_time_of_sale",
        orientation="h",barmode="group",title="Selected neighborhood/class medians — transaction mix varies")]
    if not comps.empty:
        charts.append(px.scatter(comps,x="gross_square_feet",y="sale_price",color="address",hover_data=["price_per_sqft","sale_date"],
            title="Selected recorded comparable sales — unadjusted"))
    parts=[]
    for i,chart in enumerate(charts):
        chart.update_layout(template="plotly_white",height=430,font_family="Arial")
        parts.append(chart.to_html(full_html=False,include_plotlyjs=True if i==0 else False))
    cards="".join(f'<div class="card"><small>{a}</small><strong>{b}</strong></div>' for a,b in
        [("Source scope records",f"{m['scope_rows']:,}"),("Eligible sales",f"{m['eligible_rows']:,}"),("Comparables",str(summary['count'])),("Median comparable / SF",fmt(summary['median_ppsf']))])
    html=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Property Market Research</title><style>
body{{margin:0;background:#f2f5f7;color:#172b3c;font:16px Arial}}main{{max-width:1200px;margin:auto;padding:32px 24px}}h1{{font-size:34px}}.eyebrow{{color:#126e6a;letter-spacing:2px;font-weight:bold}}.notice{{padding:18px;background:#fff1d3;border-left:4px solid #b98123;line-height:1.5}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}}.card,section{{background:white;border:1px solid #dbe3e8;padding:20px;border-radius:10px;margin:14px 0}}strong{{display:block;font-size:26px;margin-top:8px}}small{{color:#526979}}section{{overflow:auto}}table{{border-collapse:collapse;font-size:13px;width:100%}}td,th{{padding:9px;text-align:left;border-bottom:1px solid #e1e6eb}}p{{line-height:1.5}}@media(max-width:700px){{.cards{{grid-template-columns:repeat(2,1fr)}}}}</style></head><body><main>
<div class="eyebrow">MARKET RESEARCH / APPRAISER REVIEW</div><h1>Brooklyn Multifamily Sales Research</h1><p>Official NYC Department of Finance records · 2024–2025 · sale-date cutoff {m['cutoff']}</p>
<div class="notice">Research support only. No certified appraisal or opinion of market value. Source records were published after the historical sale period; arm's-length status and property condition are unverified.</div>
<div class="cards">{cards}</div><section><h2>Example subject</h2><p>{escape(s.get('address','User-supplied subject'))} · {escape(s['neighborhood'])} · class {escape(s['building_class_at_time_of_sale'])} · {s['gross_square_feet']:,.0f} gross SF</p><p>{escape(summary['status'])}. Same-parcel transfers are excluded; no price adjustments are invented.</p></section>
{''.join('<section>'+c+'</section>' for c in parts)}<section><h2>Comparable evidence schedule</h2>{records.to_html(index=False,escape=True,float_format=lambda x:f'{x:,.2f}')}</section><section><h2>Limits and review requirements</h2><p>{escape(LIMITS)}</p><p>Open appraisal_support_report.md and review_checklist.csv for research findings and outstanding verification.</p></section></main></body></html>"""
    (out/"market_dashboard.html").write_text(html)
