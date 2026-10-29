"""Prepare missing dashboard artifacts from the committed, verified source snapshot."""
from pathlib import Path
import streamlit as st
from .pipeline import run

REQUIRED = (
    'manifest.json', 'quarterly_trends.csv', 'neighborhood_summary.csv',
    'screened_sales.csv', 'quality_reconciliation.csv', 'review_exclusions.csv',
    'appraisal_support_report.md', 'review_checklist.csv',
)

@st.cache_resource(show_spinner='Preparing the official property-sales data…')
def prepare_dashboard(output_directory: str) -> Path:
    """One shared startup per directory; retain complete explicit pipeline outputs.

    Streamlit's resource cache serializes the initial build across sessions.
    Snapshot mode requires no remote downloads, secrets or manual terminal step.
    """
    out = Path(output_directory)
    if not all((out / name).is_file() for name in REQUIRED):
        run(snapshot=True, output=out)
    return out
