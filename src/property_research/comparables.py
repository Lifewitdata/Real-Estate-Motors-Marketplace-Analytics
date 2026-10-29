"""Transparent candidate screening; no unverified price adjustments."""
import numpy as np
import pandas as pd

def select_comparables(data,subject,cfg):
    as_of=pd.Timestamp(cfg["as_of_date"])
    d=data.copy()
    d["days_before_cutoff"]=(as_of-pd.to_datetime(d.sale_date)).dt.days
    d["size_difference"]=(d.gross_square_feet/subject["gross_square_feet"]-1).abs()
    d["age_difference"]=(d.year_built-subject["year_built"]).abs()
    d["unit_difference"]=(d.residential_units-subject["residential_units"]).abs()
    d["candidate_exclusions"]=""
    filters={
        "not_research_eligible":~d.eligible.astype(bool),
        "same_parcel_as_subject":d.bbl.eq(subject["bbl"]),
        "different_neighborhood":d.neighborhood.ne(subject["neighborhood"]),
        "different_building_class":d.building_class_at_time_of_sale.ne(subject["building_class_at_time_of_sale"]),
        "outside_sale_window":~d.days_before_cutoff.between(0,cfg["lookback_days"]),
        "size_mismatch":d.size_difference>cfg["max_size_difference"],
        "age_mismatch":d.age_difference>cfg["max_age_difference_years"],
        "unit_mismatch":d.unit_difference>cfg["max_unit_difference"]}
    for reason,flag in filters.items():
        d.loc[flag.fillna(True),"candidate_exclusions"]+=reason+";"
    d["candidate_exclusions"]=d.candidate_exclusions.str.rstrip(";")
    # Transparent relative similarity score, not a probability or value model.
    d["similarity_score"]=.5*d.size_difference/cfg["max_size_difference"]+\
        .2*d.age_difference/cfg["max_age_difference_years"]+\
        .2*d.days_before_cutoff/cfg["lookback_days"]+\
        .1*d.unit_difference/max(cfg["max_unit_difference"],1)
    candidates=d[d.candidate_exclusions.eq("")].sort_values(["similarity_score","record_id"])
    # Multiple transfers of a comparable parcel are not independent evidence:
    # keep its most recent qualifying sale, then rank by similarity.
    candidates=candidates.sort_values(["sale_date","record_id"],ascending=[False,True]).drop_duplicates("bbl")
    candidates=candidates.sort_values(["similarity_score","record_id"])
    selected=candidates.head(cfg["max_comparables"]).copy()
    selected["rank"]=range(1,len(selected)+1)
    d["selected"]=d.record_id.isin(selected.record_id)
    d["selection_status"]=np.select([d.selected,d.candidate_exclusions.eq("")],
        ["Selected","Eligible but not selected (rank or repeated parcel)"],default="Excluded")
    if len(selected)<cfg["minimum_comparables"]:
        summary={"status":"INSUFFICIENT COMPARABLES", "count":len(selected),
                 "median_ppsf":None,"q25_ppsf":None,"q75_ppsf":None}
    else:
        summary={"status":"APPRAISER REVIEW REQUIRED", "count":len(selected),
                 "median_ppsf":float(selected.price_per_sqft.median()),
                 "q25_ppsf":float(selected.price_per_sqft.quantile(.25)),
                 "q75_ppsf":float(selected.price_per_sqft.quantile(.75))}
    return selected,d,summary

def choose_example(data,cfg):
    """Choose a documented profile for a demonstrative research packet.

    Choose the most populated eligible class/neighborhood, then the median-sized
    2025 profile. No selection by price or valuation accuracy is performed.
    """
    eligible=data[data.eligible & (pd.to_datetime(data.sale_date).dt.year==2025)].copy()
    if eligible.empty:
        raise ValueError("No eligible 2025 property profile; supply another dataset/configuration")
    groups=eligible.groupby(["neighborhood","building_class_at_time_of_sale"]).size().reset_index(name="count")
    best=groups.sort_values(["count","neighborhood","building_class_at_time_of_sale"],ascending=[False,True,True]).iloc[0]
    pool=eligible[(eligible.neighborhood==best.neighborhood)&
                  (eligible.building_class_at_time_of_sale==best.building_class_at_time_of_sale)].copy()
    pool["distance_to_median"]=(pool.gross_square_feet-pool.gross_square_feet.median()).abs()
    row=pool.sort_values(["distance_to_median","record_id"]).iloc[0]
    fields=["record_id","source_id","source_row","bbl","address","neighborhood",
            "building_class_at_time_of_sale","gross_square_feet","year_built","residential_units"]
    return {k:(int(row[k]) if k in ["source_row","year_built","residential_units"] else
               float(row[k]) if k=="gross_square_feet" else str(row[k])) for k in fields}
