# Methodology and review controls

## Scope and screens

All thresholds live in config/research.json and are analyst assumptions, not appraisal standards. Scope is Brooklyn C1/C2/C3. Require valid location/parcel/date and finite numeric fields; sale on or before 2025-12-31; consideration at least $100,000; gross area 1,000–100,000 SF; year built 1800–2025; residential units consistent with building class; zero commercial units; price/gross SF $25–$3,000. Thresholds can exclude legitimate atypical transactions and do not establish arms-length status.

Exact repeated source content retains its first occurrence. Conflicting versions of the same apparent parcel/apartment/date/price identity are quarantined. Same-date, same-price transactions on multiple distinct parcels are held for possible package-sale review. This conservative signal can capture unrelated transactions and only operates within the scoped extract; it cannot identify every package or allocate portfolio consideration. Do not divide a potentially bundled amount by a single property's area without verification.

Every input record retains all overlapping reasons and one ordered primary reason. Primary-reason counts plus eligible count reconcile exactly to input. Excluded records remain available for review; none is silently repaired or deleted.

## Comparables

Default subject: most represented eligible 2025 neighborhood/class group, then property closest to median gross area; deterministic record-ID tie break. An example profile, not a valuation assignment or predictive validation set. Pass a JSON profile with `--subject path.json` to supply a different property; required fields are bbl, neighborhood, building_class_at_time_of_sale, gross_square_feet, year_built, residential_units. Use positive numeric area/unit/year values and uppercase source neighborhood/class labels.

Require same neighborhood/exact class, sale within 365 days of the cutoff, size within 30%, age within 20 years and unit count within three. Exclude every sale of the subject parcel. Keep the latest qualifying sale per comparable parcel and rank using:

`0.50 * relative_size_difference / 0.30 + 0.20 * age_difference / 20 + 0.20 * days_before_cutoff / 365 + 0.10 * unit_difference / 3`

Lower score means closer under these transparent assumptions; it is not a statistically calibrated model. Keep at most five. With fewer than three, withhold median and quartiles. No silent widening of geographic scope and no price-driven ranking. Median and interquartile spread describe unadjusted recorded prices, not an opinion or range of subject value.

## Reporting and validation

SQL joins eligible records to class definitions and aggregates neighborhood, quarter and class/year. Changes in observed medians reflect changing transaction mix and cannot be called appreciation or causal effects. Sparse groups and varying sales counts require caution.

The pipeline stages a complete build before publishing outputs, saves package versions/config/source registry and writes a run manifest. Tests cover policy edge cases, reconciliation and comparable selection. CI rebuilds the committed data without network downloads and smoke-tests the dashboard. A clean cached-workbook rebuild should reproduce snapshot eligible record IDs.

## Outstanding professional evidence

Verify deed consideration, package allocation, financing and arms-length status; inspect condition, location and property rights; verify units/area/zoning; obtain rent rolls, leases and expenses where an income approach is appropriate. Record appraiser-approved adjustments and reviewer signoff. This project supplies the research structure and pending checklist; it does not claim these external facts have been obtained.
