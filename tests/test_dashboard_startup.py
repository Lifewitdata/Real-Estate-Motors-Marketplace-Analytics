import json
from pathlib import Path
import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from property_research.dashboard_startup import prepare_dashboard, REQUIRED
from property_research.pipeline import ROOT

@pytest.mark.parametrize('entrypoint',['streamlit_app.py','dashboard/app.py'])
def test_fresh_checkout_starts_without_pipeline(tmp_path,monkeypatch,entrypoint):
    out=tmp_path/'not_prebuilt'
    monkeypatch.setenv('PROPERTY_OUTPUT_DIR',str(out))
    prepare_dashboard.clear()
    assert not out.exists()
    app=AppTest.from_file(str(ROOT/entrypoint)).run(timeout=90)
    assert not app.exception
    assert len(app.tabs)==4 and len(app.metric)==3
    assert all((out/name).is_file() for name in REQUIRED)
    m=json.loads((out/'manifest.json').read_text())
    assert m['scope_rows']==2373
    stamp=(out/'manifest.json').stat().st_mtime_ns
    app.selectbox[0].select('C2').run()
    assert not app.exception
    assert (out/'manifest.json').stat().st_mtime_ns==stamp
    sales=pd.read_csv(out/'screened_sales.csv')
    alternative=sales.loc[sales.eligible & sales.record_id.ne(app.selectbox[1].value),'record_id'].iloc[0]
    app.selectbox[1].set_value(alternative).run()
    assert not app.exception
    prepare_dashboard.clear()

def test_complete_outputs_not_rebuilt(tmp_path):
    # Explicit research outputs may have a custom config and must be preserved.
    for name in REQUIRED:(tmp_path/name).write_text('existing output')
    prepare_dashboard.clear()
    prepare_dashboard(str(tmp_path))
    assert (tmp_path/'manifest.json').read_text()=='existing output'
    prepare_dashboard.clear()

def test_partial_outputs_rebuilt(tmp_path):
    (tmp_path/'manifest.json').write_text('{}')
    prepare_dashboard.clear()
    prepare_dashboard(str(tmp_path))
    assert all((tmp_path/name).is_file() for name in REQUIRED)
    assert json.loads((tmp_path/'manifest.json').read_text())['scope_rows']==2373
    prepare_dashboard.clear()
