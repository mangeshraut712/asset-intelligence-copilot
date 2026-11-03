import os, sys, sqlite3, tempfile, shutil, json, pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA = os.environ.get("AIC_DATA", os.path.join(ROOT, "..", "dataset", "sample-data"))
# isolated DB so tests never touch the running server's memory
_tmp = tempfile.mkdtemp(); os.environ["AIC_DB"] = os.path.join(_tmp, "test.db"); os.environ["AIC_LLM"] = "0"
from copilot import loader
loader.DB_PATH = os.environ["AIC_DB"]
from copilot import tools
tools.DB_PATH = os.environ["AIC_DB"]

USING_SYNTHETIC = not os.path.isfile(os.path.join(DATA, "fleet", "areas.json"))

if USING_SYNTHETIC:
    # Dataset sibling missing: load an empty schema so collection does not crash.
    # Dataset-dependent tests are skipped below; pure unit tests still run.
    os.makedirs(os.path.dirname(os.environ["AIC_DB"]), exist_ok=True)
    con = sqlite3.connect(os.environ["AIC_DB"])
    con.executescript(loader.RAW_SCHEMA + loader.MEM_SCHEMA)
    con.close()
else:
    loader.load([DATA], os.environ["AIC_DB"])

def wipe():
    c = sqlite3.connect(os.environ["AIC_DB"])
    for t in ["memory_conversations", "memory_well_facts", "memory_corrections", "memory_type_rules"]: c.execute(f"DELETE FROM {t}")
    c.commit()

@pytest.fixture
def fresh():
    wipe(); yield; wipe()

def pytest_collection_modifyitems(config, items):
    if not USING_SYNTHETIC:
        return
    skip = pytest.mark.skip(
        reason="requires FlytBase sample dataset; set AIC_DATA or clone sibling ../dataset/sample-data"
    )
    pure_files = {"test_final_logic.py", "test_gemma_guard.py"}
    pure_nodes = {"test_parse_contained_hours"}
    for item in items:
        if item.path.name in pure_files or item.name in pure_nodes:
            continue
        item.add_marker(skip)
