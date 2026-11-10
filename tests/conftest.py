import os, sys, sqlite3, tempfile, json, pytest
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
DATA = os.environ.get("AIC_DATA", os.path.join(ROOT, "..", "dataset", "sample-data"))
# isolated DB so tests never touch the running server's memory
_tmp = tempfile.mkdtemp(); os.environ["AIC_DB"] = os.path.join(_tmp, "test.db"); os.environ["AIC_LLM"] = "0"
from copilot import loader
loader.DB_PATH = os.environ["AIC_DB"]
from copilot import tools
tools.DB_PATH = os.environ["AIC_DB"]

def _write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)

def build_synthetic_fleet(root):
    """Minimal sample-data layout so loader.load can populate schema + rules offline."""
    fleet = os.path.join(root, "fleet")
    _write(os.path.join(fleet, "areas.json"), json.dumps({
        "areas": [{"area_id": "NE-07", "name": "Northeast Block 7", "team_id": "TEAM-NE", "center": {"lat": 1.0, "lon": 2.0}}],
        "teams": [{"team_id": "TEAM-NE", "name": "Northeast Production", "lead_user_id": "U-1"}],
    }))
    _write(os.path.join(fleet, "users.json"), json.dumps({
        "users": [{"user_id": "U-1", "name": "Pat Lead", "role": "production_supervisor", "team_id": "TEAM-NE"}]
    }))
    _write(os.path.join(fleet, "well-types", "T200.md"), (
        "# T200\n\nWhen **producing (active)**, the wellhead must stay at least **15 °C above** ambient.\n"
        "Escalate after three corrective repairs for RCA.\n"
    ))
    _write(os.path.join(fleet, "well-types", "T350.md"), (
        "# T350\n\nWhen **producing (active)**, the wellhead must stay at least **20 °C above** ambient.\n"
        "Escalate after three corrective repairs for RCA.\n"
    ))
    _write(os.path.join(fleet, "sops", "spill-response-sop.md"), (
        "# Spill Response SOP\n\n"
        "| Class | Threshold |\n| Reportable | 5 bbl |\n| Major | 25 bbl |\n| Moderate | 1 bbl |\n\n"
        "SR-01: report within **24 hours** of discovery, or sooner if directed.\n"
        "SR-02: contained within **4 hours** of discovery.\n"
        "SR-03: verified within 60 days of containment.\n"
    ))
    _write(os.path.join(fleet, "sops", "regulatory-compliance-sop.md"), (
        "# Regulatory Compliance SOP\n\nRC-04: agency inquiries must be answered within **30 days**.\n"
    ))
    asset = os.path.join(root, "assets", "WELL-0001")
    _write(os.path.join(asset, "metadata.json"), json.dumps({
        "asset_id": "WELL-0001",
        "name": "WELL-0001",
        "well_type": "T200",
        "area_id": "NE-07",
        "team_id": "TEAM-NE",
        "in_charge_user_id": "U-1",
        "location": {"lat": 1.0, "lon": 2.0},
        "installed_on": "2010-01-01",
        "recorded_status": "active",
        "equipment": [{"equipment_id": "EQ-1", "kind": "pump_jack", "model": "X"}],
        "last_inspection": {"inspection_id": "INS-0001-0001"},
    }))
    _write(os.path.join(asset, "inspections.jsonl"), json.dumps({
        "inspection_id": "INS-0001-0001",
        "asset_id": "WELL-0001",
        "inspected_at": "2026-10-01T12:00:00Z",
        "inspector_user_id": "U-1",
        "method": "drone",
        "ambient_temp_c": 10.0,
        "wellhead_temp_c": 30.0,
        "spill_detected": False,
    }) + "\n")
    return root

_DATASET_DEPENDENT_MODULES = {
    "test_api.py",
    "test_containment.py",
    "test_examples.py",
    "test_memory.py",
    "test_pipeline_edges.py",
    "test_query.py",
    "test_raw_recompute.py",
    "test_tools.py",
    "test_unseen.py",
}

USING_SYNTHETIC = not os.path.isfile(os.path.join(DATA, "fleet", "areas.json"))
LOAD_DATA = DATA
if USING_SYNTHETIC:
    LOAD_DATA = build_synthetic_fleet(os.path.join(_tmp, "synthetic-sample-data"))

loader.load([LOAD_DATA], os.environ["AIC_DB"])

def wipe():
    c = sqlite3.connect(os.environ["AIC_DB"])
    for t in ["memory_conversations", "memory_well_facts", "memory_corrections", "memory_type_rules"]: c.execute(f"DELETE FROM {t}")
    c.commit()

@pytest.fixture
def fresh():
    wipe(); yield; wipe()

def pytest_ignore_collect(collection_path, config):
    # Avoid import-time crashes (gen_unseen, FastAPI app) when the real dataset is absent.
    if not USING_SYNTHETIC:
        return False
    name = getattr(collection_path, "name", None) or os.path.basename(str(collection_path))
    return name in _DATASET_DEPENDENT_MODULES

def pytest_collection_modifyitems(config, items):
    if not USING_SYNTHETIC:
        return
    skip = pytest.mark.skip(
        reason="requires FlytBase sample dataset; set AIC_DATA or clone sibling ../dataset/sample-data"
    )
    pure_files = {"test_final_logic.py", "test_gemma_guard.py", "test_rules_parse.py", "test_lookup_routing.py", "test_now.py", "test_parse_date.py", "test_year_to_date.py", "test_on_date_window.py", "test_relative_windows.py", "test_week_quarter_windows.py", "test_from_month_year.py", "test_between_month_year.py", "test_between_bare_months.py", "test_between_mixed_month_year.py", "test_from_to_range.py", "test_month_year_not_day.py", "test_sept_abbreviation.py", "test_month_abbreviation_period.py", "test_between_year_crossing.py", "test_between_days_of_month.py", "test_during_year_month.py", "test_previous_prior_windows.py", "test_mtd_wtd.py", "test_month_dash_range.py"}
    for item in items:
        if item.path.name in pure_files:
            continue
        item.add_marker(skip)
