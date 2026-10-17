import os, sys, sqlite3, tempfile, shutil, pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA = os.environ.get("AIC_DATA", os.path.join(ROOT, "..", "dataset", "sample-data"))
# isolated DB so tests never touch the running server's memory
_tmp = tempfile.mkdtemp(); os.environ["AIC_DB"] = os.path.join(_tmp, "test.db"); os.environ["AIC_LLM"] = "0"
from copilot import loader
loader.DB_PATH = os.environ["AIC_DB"]
from copilot import tools
tools.DB_PATH = os.environ["AIC_DB"]
loader.load([DATA], os.environ["AIC_DB"])

def wipe():
    c = sqlite3.connect(os.environ["AIC_DB"])
    for t in ["memory_conversations", "memory_well_facts", "memory_corrections", "memory_type_rules"]: c.execute(f"DELETE FROM {t}")
    c.commit()

@pytest.fixture
def fresh():
    wipe(); yield; wipe()
