"""Regression: SR-02 containment times in the WELL-0001 compliance answer.

The 11 Jun 2026 reportable spill (INS-0001-0185, report MNT-0001-029) was contained
about 7 h after discovery (breach). The separate 1 Oct 2026 moderate spill
(INS-0001-0201, report MNT-0001-032) was contained in about 1.7 h (met). Every SR-02
line must name its spill so the two numbers are never read as a contradiction.
"""
import re
from copilot import tools as T
from copilot.agent import Copilot
from copilot.loader import parse_contained_hours


def test_parse_contained_hours_variants():
    assert parse_contained_hours("the release was **contained about 7 hours after the inspection flight**") == 7.0
    assert parse_contained_hours("The release was contained about 1.7 hours after the inspection.") == 1.7
    assert parse_contained_hours("contained after 5 hours") == 5.0
    assert parse_contained_hours("contained within 90 minutes of discovery") == 1.5
    assert parse_contained_hours("held it for 4 hours with no pressure drop") is None
    assert parse_contained_hours(None) is None


def test_well_0001_sr02_times_per_spill():
    r = T.compliance("WELL-0001")
    sr02 = {i["spill"]: i["detail"] for k in ("breaches", "met") for i in r[k] if i["rule"] == "SR-02"}
    breach = [d for s, d in sr02.items() if "INS-0001-0185" in s]
    met = [d for s, d in sr02.items() if "INS-0001-0201" in s]
    assert breach and "about 7 h" in breach[0] and "MNT-0001-029" in breach[0]
    assert met and "about 1.7 h" in met[0] and "MNT-0001-032" in met[0]
    assert any(i["rule"] == "SR-02" and "INS-0001-0185" in i["spill"] for i in r["breaches"])
    assert any(i["rule"] == "SR-02" and "INS-0001-0201" in i["spill"] for i in r["met"])


def test_well_0001_answer_labels_every_sr02_line(fresh):
    text = Copilot().ask("Which rules has WELL-0001 broken in the last 12 months, and what is still open?", user="Michael Turner", chat="reg-sr02")["text"]
    lines = [l for l in text.splitlines() if "SR-02" in l]
    assert len(lines) == 2
    assert all(re.search(r"INS-0001-0\d{3}", l) for l in lines), lines
    assert any("about 7 h" in l and "INS-0001-0185" in l for l in lines)
    assert any("about 1.7 h" in l and "INS-0001-0201" in l for l in lines)
