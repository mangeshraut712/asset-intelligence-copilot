"""Keyword lookups must be answered, not stored as shared facts.

These cases run on the synthetic loader fallback, so they stay in CI when
the FlytBase sample dataset is not present.
"""
from copilot import agent
from copilot import tools as T


def test_looks_like_lookup_covers_fines_notes_and_reg_events():
    wells = ["WELL-0001"]
    for q in (
        "fines on WELL-0001 last 12 months",
        "notes on WELL-0001 last month",
        "regulatory events on WELL-0001",
        "open fines on WELL-0001",
        "WELL-0001 fines 2026",
        "repairs on WELL-0001 last 12 months",
    ):
        assert agent.looks_like_lookup(q, wells), q
    assert not agent.looks_like_lookup("WELL-0001 is shut in", wells)


def test_fines_and_notes_lookups_are_not_stored_as_facts(fresh):
    cp = agent.Copilot()
    for q in (
        "fines on WELL-0001 last 12 months",
        "notes on WELL-0001 last month",
        "regulatory events on WELL-0001",
        "open fines on WELL-0001",
        "WELL-0001 fines 2026",
    ):
        r = cp.ask(q, "U-1", "edge")
        assert "Noted for everyone" not in r["text"], q
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    r = cp.ask("WELL-0001 is shut in", "U-1", "edge")
    assert "Noted for everyone" in r["text"]


def test_looks_like_lookup_covers_alerts_production_work_orders_and_pressure():
    wells = ["WELL-0001"]
    for q in (
        "alerts on WELL-0001 last 12 months",
        "production on WELL-0001 last month",
        "work orders on WELL-0001",
        "pressure on WELL-0001",
        "open work orders on WELL-0001",
    ):
        assert agent.looks_like_lookup(q, wells), q
    assert not agent.looks_like_lookup("WELL-0001 is shut in", wells)


def test_alerts_production_and_work_order_lookups_are_not_stored_as_facts(fresh):
    cp = agent.Copilot()
    for q in (
        "alerts on WELL-0001 last 12 months",
        "production on WELL-0001 last month",
        "work orders on WELL-0001",
        "pressure on WELL-0001",
    ):
        r = cp.ask(q, "U-1", "edge")
        assert "Noted for everyone" not in r["text"], q
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    r = cp.ask("WELL-0001 is shut in", "U-1", "edge")
    assert "Noted for everyone" in r["text"]
