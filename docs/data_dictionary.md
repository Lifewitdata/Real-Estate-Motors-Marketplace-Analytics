# Data dictionary

| Fields | Meaning |
|---|---|
| record_id | SHA-256-derived stable ID for source workbook ID and original row |
| source_id, source_row | Workbook identity and 1-based original Excel row |
| borough, block, lot, bbl | NYC parcel identifiers; BBL is formatted borough-block-lot |
| address, apartment_number, zip_code | Source location information; no owner identity collected |
| neighborhood | DOF administrative neighborhood, not a geocoded radius |
| building_class_at_time_of_sale | C1/C2/C3 class used to scope and match records |
| residential_units, commercial_units, total_units | Source unit counts, screened for internal consistency |
| land_square_feet, gross_square_feet | Reported land/building area; not independently measured |
| year_built | Reported construction year; not renovation or effective age |
| sale_price, sale_date | Recorded consideration and transaction date; not verified market value |
| price_per_sqft | Recorded consideration / positive gross building area |
| exclusion_reasons, primary_exclusion, eligible | Full reasons, ordered reconciliation reason and research eligibility |
| days_before_cutoff, size_difference, age_difference, unit_difference | Explicit comparable distances in time/relative size/years/units |
| similarity_score, rank | Weighted non-price matching score and selected order |
| candidate_exclusions, selection_status | Comparable-specific exclusion/selection audit |

Nulls and nonfinite numeric data fail research screening rather than receiving invented values. Dollars are nominal USD; no inflation or time adjustment is applied. Date fields are calendar dates. See config/research.json for units and policy thresholds.
