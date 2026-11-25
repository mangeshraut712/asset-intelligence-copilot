"""parse_contained_hours (copilot/loader.py) turns free-text repair narratives into the
containment hours behind SR-02 compliance. test_containment.py needs the real dataset
(see _DATASET_DEPENDENT_MODULES in conftest), so pin the parser offline."""
from copilot.loader import parse_contained_hours


def test_hours_with_filler_words():
    assert parse_contained_hours("Spill contained within 4 hours of discovery.") == 4
    assert parse_contained_hours("contained after about 7.5 hours") == 7.5
    assert parse_contained_hours("contained after 24 hrs") == 24


def test_minutes_are_converted_to_hours():
    assert parse_contained_hours("contained in 30 minutes") == 0.5
    assert parse_contained_hours("contained in 45 mins") == 0.75


def test_markdown_bold_is_ignored():
    assert parse_contained_hours("contained within **6.5 hours** per the report") == 6.5


def test_first_narrative_match_wins_over_a_later_table_line():
    text = ("What happened: the spill was contained within about 6 hours.\n"
            "| SR-02 | contained within 8 hours |")
    assert parse_contained_hours(text) == 6


def test_no_containment_time_gives_none():
    assert parse_contained_hours("Cleanup finished; volume estimated at 3 bbl.") is None
    assert parse_contained_hours("") is None
    assert parse_contained_hours(None) is None
