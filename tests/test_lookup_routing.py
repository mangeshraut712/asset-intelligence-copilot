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


def test_looks_like_lookup_covers_emissions_vibration_corrosion_and_flow():
    wells = ["WELL-0001"]
    for q in (
        "emissions on WELL-0001 last 12 months",
        "vibration on WELL-0001",
        "corrosion on WELL-0001",
        "flow rate on WELL-0001 last month",
        "flow on WELL-0001",
    ):
        assert agent.looks_like_lookup(q, wells), q
    assert not agent.looks_like_lookup("WELL-0001 is shut in", wells)


def test_emissions_vibration_corrosion_and_flow_lookups_are_not_stored_as_facts(fresh):
    cp = agent.Copilot()
    for q in (
        "emissions on WELL-0001 last 12 months",
        "vibration on WELL-0001",
        "corrosion on WELL-0001",
        "flow rate on WELL-0001 last month",
    ):
        r = cp.ask(q, "U-1", "edge")
        assert "Noted for everyone" not in r["text"], q
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    r = cp.ask("WELL-0001 is shut in", "U-1", "edge")
    assert "Noted for everyone" in r["text"]


def test_looks_like_lookup_covers_incidents_tickets_permits_and_audits():
    wells = ["WELL-0001"]
    for q in (
        "incidents on WELL-0001",
        "tickets on WELL-0001",
        "permits on WELL-0001",
        "audits on WELL-0001",
        "open tickets on WELL-0001",
    ):
        assert agent.looks_like_lookup(q, wells), q
    assert not agent.looks_like_lookup("WELL-0001 is shut in", wells)


def test_incidents_tickets_permits_and_audits_lookups_are_not_stored_as_facts(fresh):
    cp = agent.Copilot()
    for q in (
        "incidents on WELL-0001",
        "tickets on WELL-0001",
        "permits on WELL-0001",
        "audits on WELL-0001",
    ):
        r = cp.ask(q, "U-1", "edge")
        assert "Noted for everyone" not in r["text"], q
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    r = cp.ask("WELL-0001 is shut in", "U-1", "edge")
    assert "Noted for everyone" in r["text"]


def test_looks_like_lookup_covers_inventory_telemetry_certificates_and_licenses():
    wells = ["WELL-0001"]
    for q in (
        "inventory on WELL-0001",
        "telemetry on WELL-0001",
        "certificates on WELL-0001",
        "licenses on WELL-0001",
        "open licenses on WELL-0001",
    ):
        assert agent.looks_like_lookup(q, wells), q
    assert not agent.looks_like_lookup("WELL-0001 is shut in", wells)


def test_inventory_telemetry_certificates_and_licenses_lookups_are_not_stored_as_facts(fresh):
    cp = agent.Copilot()
    for q in (
        "inventory on WELL-0001",
        "telemetry on WELL-0001",
        "certificates on WELL-0001",
        "licenses on WELL-0001",
    ):
        r = cp.ask(q, "U-1", "edge")
        assert "Noted for everyone" not in r["text"], q
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    r = cp.ask("WELL-0001 is shut in", "U-1", "edge")
    assert "Noted for everyone" in r["text"]


def test_looks_like_lookup_covers_uptime_throughput_shipments_and_documents():
    wells = ["WELL-0001"]
    for q in (
        "uptime on WELL-0001",
        "throughput on WELL-0001",
        "shipments on WELL-0001",
        "documents on WELL-0001",
        "open shipments on WELL-0001",
    ):
        assert agent.looks_like_lookup(q, wells), q
    assert not agent.looks_like_lookup("WELL-0001 is shut in", wells)


def test_uptime_throughput_shipments_and_documents_lookups_are_not_stored_as_facts(fresh):
    cp = agent.Copilot()
    for q in (
        "uptime on WELL-0001",
        "throughput on WELL-0001",
        "shipments on WELL-0001",
        "documents on WELL-0001",
    ):
        r = cp.ask(q, "U-1", "edge")
        assert "Noted for everyone" not in r["text"], q
    c = T.db()
    assert c.execute("SELECT count(*) c FROM memory_well_facts").fetchone()["c"] == 0
    r = cp.ask("WELL-0001 is shut in", "U-1", "edge")
    assert "Noted for everyone" in r["text"]
