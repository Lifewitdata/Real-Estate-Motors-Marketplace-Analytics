# Real Estate Market Research & Comparable Sales

## Assignment and scope
Educational acquisition/disposition research-support scenario: Brooklyn walk-up apartment buildings, classes C1, C2 and C3. Sale-date cutoff: **2025-12-31**. No actual client, inspection, appraiser review or lending decision is claimed.

## Data and quality
Official source extract: **2,373 records**; **1,045 research-eligible sales**; **1,328 flagged/excluded records**. Reasons reconcile to the input count in quality_reconciliation.csv. Screens retain a separate review file; they do not certify that retained sales are arm's length. Repeated same-date consideration across distinct parcels is held for possible package-sale review; unrelated sales may also be flagged. Detection is limited to the committed property-class scope and cannot identify every package. Third-party provenance and publisher notes are in manifest.json and docs/sources.md.

## Example subject profile
Address: **48 ROCKAWAY PARKWAY**. BBL: 3-04599-0030. Neighborhood: FLATBUSH-NORTH. Class: C3. Gross area: 3,214 square feet. Residential units: 4. Year built: 1930.

The default profile is selected deterministically from the most represented eligible 2025 neighborhood/class group, choosing its median-sized profile. It is an illustrative recorded property, not a client assignment. Its sale price is not an input to selection and every sale of its parcel is withheld from the comparable pool.

## Comparable screening
Require the same neighborhood and exact class, a recorded sale within 365 days before the cutoff, gross area within 30%, construction year within 20 years, and unit count within 3. Keep at most one recent qualifying sale per parcel. Rank eligible candidates by a documented size/age/recency/unit similarity score. No price-based ranking, undisclosed relaxation or invented adjustments are used.

**Status: APPRAISER REVIEW REQUIRED**. Selected comparable count: **5**.
Observed unadjusted comparable median: **$351.78/gross square foot**.
Observed interquartile spread: **$223.58–$359.60/gross square foot**.
These are descriptive statistics of selected transactions, not a value range or concluded subject value. With fewer than three comparables, statistics are withheld. See appraiser_comparable_schedule.csv for the source-traceable schedule and comparable_audit.csv for each candidate's selection/exclusion rationale.

## Next actions for supervised report preparation
1. Confirm source record/deed and whether each transaction is arm's length, bundled or subject to unusual financing.
2. Verify subject and comparable area, units, condition, renovations, tenancy, zoning and property rights with authorised sources.
3. Ask the supervising appraiser whether location, condition, size or time adjustments are supportable; document evidence before applying them.
4. Obtain verified rents, expenses, leases and occupancy before considering an income approach. No implied cap rate is calculated here.
5. Record reviewer identity, date, acceptance/rejection of each comparable and unresolved evidence before any appraisal conclusion.

## Limitations
This packet supports research under an appraiser's supervision. It is not a certified appraisal or an opinion of market value. Recorded consideration is not verified arm's-length consideration. No transaction terms, financing, condition, inspection, rent roll, NOI, lease terms, occupancy, cap rate, zoning verification or professional adjustments are available. No income or cost approach is fabricated. Neighborhood matches are administrative geography, not a verified distance radius. Area and unit figures require verification. Later-released 2024/2025 workbooks supply historical sale records and roll-based attributes; this is not a point-in-time reconstruction of information available at the stated sale-date cutoff. Changing quarterly medians can reflect the composition of properties sold, not appreciation of a fixed property.
