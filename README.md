# Real Estate Market Research & Comparable Sales

An executable Python/SQL research project for supervised real estate appraisal support: collect official transaction records, document their provenance, screen data quality, compare properties and prepare a review packet.

**Verified dataset:** 2,373 Brooklyn walk-up apartment sales records from NYC Department of Finance annual 2024/2025 workbooks. The default policy retains 1,045 research-eligible records and preserves 1,328 excluded records for review. These are descriptive research screens, not verified arm's-length sales or appraised values.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m pip install -e '.[dev]'
python -m property_research.pipeline --snapshot
streamlit run dashboard/app.py
python -m pytest -q
```

The committed extract supports reproducible offline runs. To rebuild from the official workbooks, run `python -m property_research.pipeline --download`. Upstream files may change; inspect the new source hashes and counts. Raw workbooks and generated outputs are ignored by Git.

## Deliverables

- Four-tab Streamlit dashboard: market trends, comparable screening, data quality and research report.
- Standalone interactive `outputs/market_dashboard.html`.
- Persistent DuckDB database and executable SQL for neighborhood, property-class and quarterly summaries.
- Comparable schedule with source workbook/row, recorded consideration, gross area and unadjusted price per square foot.
- Every-row exclusion audit and reconciliation; duplicate, conflicting identity and possible package-sale checks.
- Appraisal-support report and pending evidence/reviewer checklist.

[View the example research report](reports/appraisal_support_report.md) · [Comparable schedule](reports/appraiser_comparable_schedule.csv) · [Quality reconciliation](reports/quality_reconciliation.csv)

## Relevance to appraisal research

| Role responsibility | Project evidence |
|---|---|
| Collect external market information | Official workbook acquisition, SHA-256 provenance and original row references |
| Aggregate and interpret market data | Python quality controls and SQL segmentation/trend summaries |
| Assist report preparation | Comparable schedule, research narrative and unresolved-evidence checklist |
| Understand research databases/software | DuckDB relational reporting, Python pipeline and Streamlit dashboard |
| Support senior reviewer decisions | Explicit selection/exclusion rationale and no unsupported valuation conclusion |

## Method and limitations

Scope: Brooklyn classes C1 (over six families without stores), C2 (five to six families), C3 (four families). The example subject is a deterministic median-sized profile, not a client assignment. Comparable candidates must match neighborhood and class, pass size/age/unit/time tolerances and exclude the subject's parcel. At least three are required before reporting descriptive statistics. No sale-price-based ranking or fabricated adjustments are used.

The workbooks were published after the historical sale period. The 2025-12-31 cutoff filters sale dates; this is **not** a point-in-time historical valuation. No internal company database, CoStar access, inspection, rent roll, NOI, cap rate or certified appraisal is claimed. A supervising appraiser must verify transaction terms, property condition and adjustments.

[Sources](docs/sources.md) · [Methodology and controls](docs/methodology.md) · [Data dictionary](docs/data_dictionary.md)

## Validation

17 tests cover exclusions, duplicate/conflicting records, possible package consideration, same-parcel removal, price-independent ranking, insufficient comparable handling, SQL reconciliation and source traceability. GitHub Actions runs tests, rebuilds the snapshot report and smoke-tests all four dashboard tabs. Tests demonstrate software behavior, not appraisal accuracy.

The original hardcoded marketplace walkthrough is preserved in [legacy/](legacy/) for historical context. It is not the analytical evidence for this project.
