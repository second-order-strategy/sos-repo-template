"""Starter tests. They prove the template runs end to end (Handoff Test, CS-03.4)."""

import datetime

import pytest
from check_commits import check_commit
from check_manifest import validate_manifest

from sos_app import describe_project

VALID = {
    "profile": "sandbox",
    "classification": "public",
    "linear": {"team_key": "AI", "issue": "AI-1"},
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
    assert check_commit("Jerome Davis", "Fix typo", "AI")


def test_agent_commit_needs_agent_trailer():
    assert check_commit("sos-agents[bot]", "Add parser\n\nRefs AI-12", "AI")
    assert check_commit("sos-agents[bot]", "Add parser\n\nRefs AI-12\nAgent: builder", "AI") == []
