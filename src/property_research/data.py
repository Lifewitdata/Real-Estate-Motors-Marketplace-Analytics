"""Official-source acquisition, normalization and traceable research screening."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
import numpy as np
import pandas as pd

SOURCE_PAGE="https://www.nyc.gov/site/finance/property/property-annualized-sales-update.page"
CLASS_URL="https://www.nyc.gov/assets/finance/jump/hlpbldgcode.html"
GLOSSARY_URL="https://www.nyc.gov/assets/finance/downloads/pdf/07pdf/glossary_rsf071607.pdf"
FIELDS=["borough","neighborhood","block","lot","address","apartment_number","zip_code",
        "residential_units","commercial_units","total_units","land_square_feet","gross_square_feet",
        "year_built","building_class_at_time_of_sale","sale_price","sale_date"]
NUMERIC=["borough","block","lot","residential_units","commercial_units","total_units",
         "land_square_feet","gross_square_feet","year_built","sale_price"]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def normalize(path,source_id):
    path=Path(path)
    top=pd.read_excel(path,header=None,nrows=20)
    rows=top.index[top.iloc[:,0].astype(str).str.strip().eq("BOROUGH")]
    if len(rows)!=1:
        raise ValueError(f"Expected one BOROUGH header in {path.name}")
    header=int(rows[0])
    d=pd.read_excel(path,header=header)
    d.columns=[re.sub(r"[^a-z0-9]+","_",str(c).strip().lower()).strip("_") for c in d.columns]
    if set(FIELDS)-set(d.columns):
        raise ValueError(f"Missing fields: {set(FIELDS)-set(d.columns)}")
    d["source_row"]=d.index+header+2
    d=d[d[FIELDS].notna().any(axis=1)].copy()
    d=d[FIELDS+["source_row"]]
    for field in NUMERIC:
        d[field]=pd.to_numeric(d[field],errors="coerce")
    for field in ["neighborhood","address","building_class_at_time_of_sale"]:
        d[field]=d[field].fillna("").astype(str).str.strip().str.upper()
    d["apartment_number"]=d.apartment_number.fillna("").astype(str).str.strip()
    d["zip_code"]=d.zip_code.fillna("").astype(str).str.replace(r"\.0$","",regex=True)
    d["sale_date"]=pd.to_datetime(d.sale_date,errors="coerce").dt.normalize()
    d["source_id"]=source_id
    d["record_id"]=[hashlib.sha256(f"{source_id}:{n}".encode()).hexdigest()[:20] for n in d.source_row]
    d["bbl"]=d[["borough","block","lot"]].apply(
        lambda r: f"{int(r.iloc[0])}-{int(r.iloc[1]):05d}-{int(r.iloc[2]):04d}" if r.notna().all() else "",axis=1)
    d["price_per_sqft"]=d.sale_price/d.gross_square_feet.replace(0,np.nan)
    return d

def acquire(raw_dir,download=False):
    raw=Path(raw_dir)
    raw.mkdir(parents=True,exist_ok=True)
    registry=[]; frames=[]
    for year in [2024,2025]:
        name=f"{year}_brooklyn.xlsx"
        path=raw/name
        url=f"https://www.nyc.gov/assets/finance/downloads/pdf/rolling_sales/annualized-sales/{year}/{name}"
        if download:
            with urlopen(Request(url,headers={"User-Agent":"PropertyResearchPortfolio/1.0"}),timeout=60) as response:
                path.write_bytes(response.read())
        if not path.exists():
            raise FileNotFoundError(f"Missing {path}. Run with --download or use --snapshot.")
        sid=f"nyc_dof_brooklyn_{year}"
        metadata=pd.read_excel(path,header=None,nrows=6).iloc[:,0].dropna().astype(str).tolist()
        d=normalize(path,sid); frames.append(d)
        registry.append(dict(source_id=sid,provider="NYC Department of Finance",url=url,
            landing_page=SOURCE_PAGE,file_name=name,sha256=digest(path),rows=len(d),
            verified_at_utc=datetime.now(timezone.utc).isoformat(),publisher_notes=metadata))
    return pd.concat(frames,ignore_index=True),registry

def screen(data,cfg):
    """Preserve every input row, with overlapping reasons and one primary reason."""
    d=data.copy()
    for c in NUMERIC:
        d[c]=pd.to_numeric(d[c],errors="coerce")
    d["sale_date"]=pd.to_datetime(d.sale_date,errors="coerce")
    d["price_per_sqft"]=d.sale_price/d.gross_square_feet.replace(0,np.nan)
    key=["bbl","apartment_number","sale_date","sale_price"]
    # Exact repeated source content is deduplicated; conflicting apparent sale
    # identities are quarantined because the feed has no deed-level event ID.
    exact=d.duplicated(subset=FIELDS,keep="first")
    distinct=d.loc[~exact].groupby(key,dropna=False)["record_id"].transform("size")
    conflict=pd.Series(False,index=d.index)
    conflict.loc[distinct.index]=distinct.gt(1)
    # A repeated consideration on distinct parcels is a review signal, not proof.
    parcel_count=d.groupby(["sale_date","sale_price"],dropna=False)["bbl"].transform("nunique")
    possible_package=parcel_count.gt(1)&d.sale_price.ge(cfg["min_price"])
    rules={
        "outside_scope":~d.building_class_at_time_of_sale.isin(cfg["focus_classes"]),
        "invalid_parcel":d.bbl.eq("")|d.borough.ne(cfg["borough"]),
        "missing_location":d.neighborhood.fillna("").eq("")|d.address.fillna("").eq(""),
        "invalid_date":d.sale_date.isna(),
        "after_cutoff":d.sale_date>pd.Timestamp(cfg["as_of_date"]),
        "missing_or_nonfinite_numeric":~np.isfinite(d[NUMERIC]).all(axis=1),
        "zero_or_negative_price":d.sale_price.le(0),
        "low_consideration_review":d.sale_price.gt(0)&d.sale_price.lt(cfg["min_price"]),
        "gross_area_outside_screen":~d.gross_square_feet.between(cfg["min_gross_sqft"],cfg["max_gross_sqft"]),
        "invalid_year":~d.year_built.between(cfg["min_year_built"],pd.Timestamp(cfg["as_of_date"]).year),
        "mixed_or_invalid_units":d.commercial_units.ne(0)|d.residential_units.lt(4)|
            d.residential_units.ne(d.total_units)|d.residential_units.mod(1).ne(0),
        "unit_class_mismatch":(d.building_class_at_time_of_sale.eq("C3")&d.residential_units.ne(4))|
            (d.building_class_at_time_of_sale.eq("C2")&~d.residential_units.between(5,6))|
            (d.building_class_at_time_of_sale.eq("C1")&d.residential_units.le(6)),
        "ppsf_outside_screen":~d.price_per_sqft.between(cfg["min_ppsf"],cfg["max_ppsf"]),
        "possible_multi_parcel_consideration":possible_package,
        "conflicting_sale_identity":conflict,
        "exact_duplicate":exact}
    d["exclusion_reasons"]=""
    d["primary_exclusion"]=""
    for reason,flag in rules.items():
        flag=flag.fillna(True)
        d.loc[flag,"exclusion_reasons"]+=reason+";"
        d.loc[flag&d.primary_exclusion.eq(""),"primary_exclusion"]=reason
    d["exclusion_reasons"]=d.exclusion_reasons.str.rstrip(";")
    d["eligible"]=d.primary_exclusion.eq("")
    return d
