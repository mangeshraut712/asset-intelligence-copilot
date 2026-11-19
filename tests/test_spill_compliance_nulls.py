"""Nullable reg_events fields must not crash spill compliance."""
import sqlite3

from copilot import tools


def _db(hours_to_report, fine_usd):
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    c.executescript(
        """
        CREATE TABLE rules (key TEXT, value REAL, source TEXT);
        CREATE TABLE reg_events (event_id TEXT, related_inspection_id TEXT, event_type TEXT,
            protocol_id TEXT, date TEXT, status TEXT, detail TEXT, hours_to_report REAL, fine_usd REAL);
        CREATE TABLE maintenance (maintenance_id TEXT, triggered_by_inspection_id TEXT,
            contained_hours REAL, report_text TEXT);
        """
    )
    c.executemany(
        "INSERT INTO reg_events VALUES (?,?,?,?,?,?,?,?,?)",
        [
            ("EV-1", "INS-1", "spill_report_filed", "SR-01", "2026-09-02", "closed", "", hours_to_report, None),
            ("EV-2", "INS-1", "notice_of_violation", "SR-01", "2026-09-10", "open", "", None, fine_usd),
            ("EV-3", "INS-1", "nov_response_filed", "RC-04", "2026-09-20", "closed", "", None, None),
        ],
    )
    return c


def _row():
    return {"inspection_id": "INS-1", "spill_est_volume_bbl": 10, "inspected_at": "2026-09-01T08:00:00Z"}


def test_missing_hours_to_report_is_open_not_a_crash():
    out = tools.spill_compliance(_db(None, 5000), _row())
    sr01 = [item for item in out["open"] if item["rule"] == "SR-01" and "EV-1" in item["detail"]]
    assert sr01 and "not recorded" in sr01[0]["detail"]
    assert not [item for item in out["breaches"] + out["met"] if item["rule"] == "SR-01"]


def test_open_notice_without_fine_is_reported():
    out = tools.spill_compliance(_db(3, None), _row())
    nov = [item for item in out["open"] if "EV-2" in item["detail"]]
    assert nov and "fine not recorded" in nov[0]["detail"]
    assert [item for item in out["met"] if item["rule"] == "SR-01"]
