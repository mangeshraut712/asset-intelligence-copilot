import os

from copilot import loader


def _fleet(tmp_path, rca_line):
    wt = tmp_path / "fleet" / "well-types"
    wt.mkdir(parents=True)
    (wt / "T900.md").write_text(
        "When **producing (active)**, keep at least **12 °C above** ambient.\n" + rca_line + "\n"
    )
    sops = tmp_path / "fleet" / "sops"
    sops.mkdir()
    (sops / "spill-response-sop.md").write_text("no thresholds here\n")
    (sops / "regulatory-compliance-sop.md").write_text("no deadlines here\n")
    return os.fspath(tmp_path / "fleet")


def _rca(rules):
    return dict((k, v) for k, v, _ in rules)["T900.rca_repairs"]


def test_rca_threshold_accepts_number_words_and_digits(tmp_path):
    for line, want in [
        ("- Two or more **corrective** events trigger RCA.", 2),
        ("- Four or more **corrective** events trigger RCA.", 4),
        ("- 5 or more **corrective** events trigger RCA.", 5),
        ("RCA after two corrective events on one kind.", 2),
    ]:
        sub = tmp_path / str(want) / line[:3].strip("- ")
        assert _rca(loader.parse_rules(_fleet(sub, line))) == want


def test_rca_threshold_falls_back_instead_of_crashing(tmp_path):
    rules = loader.parse_rules(_fleet(tmp_path, "- Several or more **corrective** events."))
    assert _rca(rules) == 3
