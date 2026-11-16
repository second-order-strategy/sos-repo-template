"""Starter tests. They prove the template runs end to end (Handoff Test, CS-03.4)."""

import datetime

import pytest
from check_commits import check_commit
from check_manifest import validate_manifest

from sos_app import describe_project

VALID = {
    "standard": "SOS-EOS-001 v1.0",
    "overlays": [],
    "profile": "sandbox",
    "classification": "public",
    "linear": {"team_key": "SOS", "issue": "SOS-1"},
    "expiry": datetime.date.today() + datetime.timedelta(days=30),
    "owners": {r: "Owner" for r in ("outcome", "engineering", "release", "operational")},
}


def test_describe_project_names_the_project():
    assert describe_project("Triage") == "Triage is a Second Order Strategy project."


def test_describe_project_rejects_empty_name():
    with pytest.raises(ValueError):
        describe_project("  ")


def test_valid_manifest_passes():
    assert validate_manifest(VALID) == []


def test_expired_sandbox_fails():
    data = {**VALID, "expiry": datetime.date(2020, 1, 1)}
    assert any("expired" in p for p in validate_manifest(data))


def test_unknown_profile_fails():
    assert validate_manifest({**VALID, "profile": "yolo"})


def test_commit_without_linear_issue_fails():
    assert check_commit("Jerome Davis", "Fix typo", "SOS")


def test_agent_commit_needs_agent_trailer():
    agent = "sos-agents-app[bot]"
    assert check_commit(agent, "Add parser\n\nRefs SOS-12", "SOS")
    assert check_commit(agent, "Add parser\n\nRefs SOS-12\nAgent: builder", "SOS") == []


@pytest.mark.parametrize("data", [None, [], "sandbox", {"profile": []}])
def test_invalid_manifest_shape_reports_problems(data):
    assert validate_manifest(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("standard", "unknown"),
        ("overlays", ["ai", "extra"]),
        ("overlays", ["data", "data"]),
        ("overlays", "ai"),
        ("owners", ["Owner"]),
        ("owners", {**VALID["owners"], "engineering": "   "}),
        ("linear", "SOS-1"),
        ("linear", {"team_key": "SOS", "issue": "AI-1"}),
        ("linear", {"team_key": "SOS\n", "issue": "SOS-1"}),
        ("expiry", datetime.datetime(2099, 1, 1)),
        ("expiry", "2027-02-30"),
    ],
)
def test_manifest_rejects_unusable_registration_fields(field, value):
    assert validate_manifest({**VALID, field: value})


def test_sandbox_accepts_quoted_iso_date():
    assert validate_manifest({**VALID, "expiry": VALID["expiry"].isoformat()}) == []


@pytest.mark.parametrize("author", ["sos-agents-app[bot]", "sos-agents[bot]"])
def test_agent_line_in_message_body_is_not_a_trailer(author):
    assert check_commit(author, "SOS-12\n\nAgent: builder\n\nAdditional context", "SOS")
    assert check_commit(author, "SOS-12\n\nAgent: builder", "SOS") == []
