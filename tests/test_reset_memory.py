import sqlite3

from copilot import loader


def test_reset_memory_clears_every_memory_table_including_prefs(tmp_path):
    con = sqlite3.connect(tmp_path / "m.db")
    con.execute("CREATE TABLE memory_conversations(id INTEGER PRIMARY KEY, user_id TEXT)")
    con.execute("CREATE TABLE memory_prefs(user_id TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE wells(asset_id TEXT)")
    con.execute("INSERT INTO memory_conversations(user_id) VALUES('U-1')")
    con.execute("INSERT INTO memory_prefs VALUES('U-1', '{\"sort_area_well\": true}')")
    con.execute("INSERT INTO wells VALUES('WELL-0001')")

    loader.reset_memory(con)

    assert con.execute("SELECT COUNT(*) FROM memory_conversations").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM memory_prefs").fetchone()[0] == 0
    assert con.execute("SELECT COUNT(*) FROM wells").fetchone()[0] == 1


def test_reset_memory_drop_removes_memory_tables(tmp_path):
    con = sqlite3.connect(tmp_path / "m.db")
    con.execute("CREATE TABLE memory_prefs(user_id TEXT PRIMARY KEY, value TEXT)")
    con.execute("CREATE TABLE wells(asset_id TEXT)")

    loader.reset_memory(con, drop=True)

    names = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert names == {"wells"}
