"""python -m property_research.pipeline --snapshot or --download."""
import argparse
from datetime import datetime,timezone
import importlib.metadata
import json
import os
from pathlib import Path
import tempfile
import duckdb
import pandas as pd
from .data import acquire,screen,digest,CLASS_URL,GLOSSARY_URL,SOURCE_PAGE
from .comparables import select_comparables,choose_example
from .reporting import write_reports

ROOT=Path(__file__).resolve().parents[2]

def run(snapshot=False,download=False,output="outputs",subject_path=None,config_path=None):
    cfg=json.loads(Path(config_path or ROOT/"config/research.json").read_text())
    if not (cfg["max_size_difference"]>0 and cfg["max_age_difference_years"]>0 and cfg["lookback_days"]>0
            and cfg["minimum_comparables"]>=3 and cfg["max_comparables"]>=cfg["minimum_comparables"]):
        raise ValueError("Invalid screening configuration")
    if snapshot:
        path=ROOT/"data/brooklyn_multifamily_sales.csv"
        data=pd.read_csv(path,keep_default_na=False)
        registry=json.loads((ROOT/"data/sources.json").read_text())
        if digest(path)!=registry["snapshot_sha256"]:
            raise ValueError("Committed source snapshot hash mismatch")
        expected=sum(x["scope_rows"] for x in registry["sources"])
        if len(data)!=expected:
            raise ValueError("Source row-count reconciliation failed")
        mode="OFFICIAL NYC DOF DATA — COMMITTED C1/C2/C3 EXTRACT"
    else:
        all_sales,sources=acquire(ROOT/"data/raw",download)
        data=all_sales[all_sales.building_class_at_time_of_sale.isin(cfg["focus_classes"])].copy()
        if data.empty: raise ValueError("No in-scope records in source workbooks")
        references=[]
        from urllib.request import urlopen
        for name,url in [("building_classes.html",CLASS_URL),("sales_glossary.pdf",GLOSSARY_URL)]:
            p=ROOT/"data/raw"/name
            if download:
                with urlopen(url,timeout=60) as response:p.write_bytes(response.read())
            if not p.exists():raise FileNotFoundError(f"Missing {p}; run with --download")
            references.append(dict(file_name=name,url=url,sha256=digest(p)))
        for s in sources:
            s["scope_rows"]=int(data.source_id.eq(s["source_id"]).sum())
        registry=dict(sources=sources,references=references,scope="Brooklyn class at time of sale C1/C2/C3",
            all_borough_rows=len(all_sales),out_of_scope_rows=len(all_sales)-len(data),
            generated_at_utc=datetime.now(timezone.utc).isoformat())
        mode="OFFICIAL NYC DOF DATA — SOURCE WORKBOOK REBUILD"
    screened=screen(data,cfg)
    if not screened.record_id.is_unique:raise ValueError("Source IDs are not unique")
    eligible=screened[screened.eligible].copy()
    if eligible.empty:raise ValueError("No sales pass research screens")
    subject=json.loads(Path(subject_path).read_text()) if subject_path else choose_example(screened,cfg)
    for key in ["bbl","neighborhood","building_class_at_time_of_sale","gross_square_feet","year_built","residential_units"]:
        if key not in subject:raise ValueError(f"Subject missing {key}")
    if subject["gross_square_feet"]<=0:raise ValueError("Subject area must be positive")
    selected,audit,summary=select_comparables(screened,subject,cfg)
    out=Path(output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".research-build-",dir=out.parent) as temporary:
        stage=Path(temporary)
        screened.to_csv(stage/"screened_sales.csv",index=False)
        eligible.to_csv(stage/"eligible_sales.csv",index=False)
        screened[~screened.eligible].to_csv(stage/"review_exclusions.csv",index=False)
        primary=screened.groupby("primary_exclusion",dropna=False).size().reset_index(name="rows")
        primary["primary_exclusion"]=primary.primary_exclusion.replace("","eligible")
        primary.to_csv(stage/"quality_reconciliation.csv",index=False)
        selected.to_csv(stage/"comparable_sales.csv",index=False)
        audit.to_csv(stage/"comparable_audit.csv",index=False)
        con=duckdb.connect(str(stage/"research.duckdb"))
        try:
            con.register("source_frame",screened)
            con.execute("CREATE TABLE screened_sales AS SELECT * FROM source_frame")
            con.register("class_frame",pd.read_csv(ROOT/"config/building_classes.csv"))
            con.execute("CREATE TABLE class_lookup AS SELECT * FROM class_frame")
            con.execute((ROOT/"sql/market_research.sql").read_text())
            for table in ["neighborhood_summary","quarterly_trends","year_class_comparison"]:
                con.execute(f"SELECT * FROM {table}").df().to_csv(stage/f"{table}.csv",index=False)
            assert con.execute("SELECT COUNT(*) FROM research_sales").fetchone()[0]==len(eligible)
        finally:con.close()
        manifest=dict(mode=mode,scope_rows=len(screened),eligible_rows=len(eligible),excluded_rows=int((~screened.eligible).sum()),
            cutoff=cfg["as_of_date"],config=cfg,subject=subject,comparables=summary,sources=registry,
            versions={p:importlib.metadata.version(p) for p in ["pandas","numpy","duckdb","openpyxl"]},
            source_content_sha256=__import__('hashlib').sha256(screened.to_csv(index=False).encode()).hexdigest(),
            decision="Research support for appraiser review; no market value opinion concluded")
        write_reports(stage,manifest,selected)
        (stage/"manifest.json").write_text(json.dumps(manifest,indent=2))
        out.mkdir(exist_ok=True)
        for p in sorted(stage.iterdir(),key=lambda p:p.name=="manifest.json"):
            if p.name=="research.duckdb":(out/"research.duckdb.wal").unlink(missing_ok=True)
            os.replace(p,out/p.name)
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--snapshot",action="store_true",help="Use the hash-verified committed official-data extract")
    p.add_argument("--download",action="store_true",help="Fetch official XLSX and reference documents")
    p.add_argument("--output",default="outputs")
    p.add_argument("--subject",type=Path)
    p.add_argument("--config",type=Path)
    args=p.parse_args()
    if args.snapshot and args.download:p.error("Choose snapshot or download, not both")
    m=run(args.snapshot,args.download,args.output,args.subject,args.config)
    print(json.dumps({k:m[k] for k in ["mode","scope_rows","eligible_rows","excluded_rows","subject","comparables"]},indent=2))

if __name__=="__main__":main()
