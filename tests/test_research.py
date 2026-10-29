import json
from pathlib import Path
import duckdb
import pandas as pd
import pytest
from property_research.data import screen
from property_research.comparables import select_comparables
from property_research.pipeline import ROOT,run

@pytest.fixture
def cfg():return json.loads((ROOT/"config/research.json").read_text())

@pytest.fixture
def sample():
    return pd.DataFrame([dict(borough=3,neighborhood="TEST",block=i+1,lot=1,address=f"{i} TEST ST",apartment_number="",
        zip_code="11201",residential_units=4,commercial_units=0,total_units=4,land_square_feet=2000,
        gross_square_feet=4000+i*100,year_built=1920,building_class_at_time_of_sale="C3",sale_price=1500000+i*10000,
        sale_date=f"2025-0{i+1}-01",source_id="fixture",source_row=i+9,record_id=f"R{i}",bbl=f"3-{i+1:05d}-0001") for i in range(6)])

@pytest.fixture
def subject():return dict(bbl="3-99999-0001",neighborhood="TEST",building_class_at_time_of_sale="C3",
                           gross_square_feet=4200,year_built=1920,residential_units=4)

@pytest.mark.parametrize("field,value,reason",[
    ("sale_price",0,"zero_or_negative_price"),("sale_price",50000,"low_consideration_review"),
    ("gross_square_feet",0,"gross_area_outside_screen"),("year_built",0,"invalid_year"),
    ("commercial_units",1,"mixed_or_invalid_units"),("residential_units",6,"unit_class_mismatch"),
    ("sale_date","2026-01-01","after_cutoff"),("borough",1,"invalid_parcel")])
def test_screens_flag_records(sample,cfg,field,value,reason):
    sample.loc[0,field]=value
    d=screen(sample,cfg)
    assert not d.loc[0,"eligible"] and reason in d.loc[0,"exclusion_reasons"]

def test_exact_duplicates_and_conflicts_are_distinct(sample,cfg):
    duplicate=sample.iloc[[0]].copy();duplicate["record_id"]="COPY"
    d=screen(pd.concat([sample,duplicate],ignore_index=True),cfg)
    assert d.exclusion_reasons.str.contains("exact_duplicate").sum()==1
    conflict=duplicate.copy();conflict["address"]="CONFLICTING ADDRESS"
    d=screen(pd.concat([sample,conflict],ignore_index=True),cfg)
    assert d.exclusion_reasons.str.contains("conflicting_sale_identity").sum()==2

def test_subject_and_future_sales_never_selected(sample,cfg,subject):
    subject["bbl"]=sample.loc[0,"bbl"]
    sample.loc[1,"sale_date"]="2026-01-01"
    selected,audit,summary=select_comparables(screen(sample,cfg),subject,cfg)
    assert not selected.bbl.eq(subject["bbl"]).any()
    assert (pd.to_datetime(selected.sale_date)<=pd.Timestamp(cfg["as_of_date"])).all()
    assert audit.loc[0,"candidate_exclusions"].find("same_parcel_as_subject")>=0

def test_insufficient_comparables_withhold_statistics(sample,cfg,subject):
    selected,audit,summary=select_comparables(screen(sample.head(2),cfg),subject,cfg)
    assert summary["status"]=="INSUFFICIENT COMPARABLES" and summary["median_ppsf"] is None

def test_comparable_price_does_not_drive_ranking(sample,cfg,subject):
    first=select_comparables(screen(sample,cfg),subject,cfg)[0].record_id.tolist()
    sample.sale_price=sample.sale_price.iloc[::-1].to_numpy()
    second=select_comparables(screen(sample,cfg),subject,cfg)[0].record_id.tolist()
    assert first==second

def test_no_silent_neighborhood_relaxation(sample,cfg,subject):
    subject["neighborhood"]="DIFFERENT"
    selected,_,summary=select_comparables(screen(sample,cfg),subject,cfg)
    assert selected.empty and summary["median_ppsf"] is None

def test_one_comparable_sale_per_parcel(sample,cfg,subject):
    sample.loc[1,"bbl"]=sample.loc[0,"bbl"]
    selected,_,_=select_comparables(screen(sample,cfg),subject,cfg)
    assert selected.bbl.is_unique
    assert "R0" not in selected.record_id.tolist()

@pytest.fixture(scope="module")
def completed(tmp_path_factory):
    out=tmp_path_factory.mktemp("property_run")
    m=run(snapshot=True,output=out)
    return out,m

def test_official_snapshot_reconciliation_and_sql(completed):
    out,m=completed
    quality=pd.read_csv(out/"quality_reconciliation.csv")
    assert quality.rows.sum()==m["scope_rows"]==m["eligible_rows"]+m["excluded_rows"]
    eligible=pd.read_csv(out/"eligible_sales.csv")
    with duckdb.connect(str(out/"research.duckdb")) as con:
        con.execute((ROOT/"sql/market_research.sql").read_text())
        assert con.execute("SELECT COUNT(*) FROM research_sales").fetchone()[0]==len(eligible)
        assert con.execute("SELECT SUM(sales) FROM neighborhood_summary").fetchone()[0]==len(eligible)
    assert eligible.record_id.is_unique
    assert (eligible.sale_price>0).all() and (eligible.gross_square_feet>0).all()

def test_comparable_source_trace_and_report(completed):
    out,m=completed
    selected=pd.read_csv(out/"comparable_sales.csv")
    assert selected.bbl.is_unique and not selected.bbl.eq(m["subject"]["bbl"]).any()
    assert selected.source_row.notna().all()
    assert set(selected.source_id)<=set(s["source_id"] for s in m["sources"]["sources"])
    report=(out/"appraisal_support_report.md").read_text()
    assert "not a certified appraisal" in report
    assert "No actual client" in report
    assert (out/"market_dashboard.html").stat().st_size>10000


def test_repeated_consideration_requires_review(sample,cfg):
    sample.loc[1,"sale_date"]=sample.loc[0,"sale_date"]
    sample.loc[1,"sale_price"]=sample.loc[0,"sale_price"]
    result=screen(sample,cfg)
    assert not result.loc[:1,"eligible"].any()
    assert result.loc[:1,"exclusion_reasons"].str.contains("possible_multi_parcel").all()
