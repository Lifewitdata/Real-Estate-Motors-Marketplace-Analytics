"""Streamlit Community Cloud entrypoint; also supports `streamlit run streamlit_app.py`."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parent / 'dashboard' / 'app.py'), run_name='__main__')
