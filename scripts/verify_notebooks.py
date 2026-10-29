"""Execute all notebooks from a clean kernel; fail on any cell error."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
    nb=nbformat.read(path,as_version=4)
    NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
    print(f'Executed {path.name}: {sum(c.cell_type=="code" for c in nb.cells)} code cells')
