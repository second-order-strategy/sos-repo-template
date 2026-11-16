"""Exercise the manifest and commit checks at their CI entry points."""

import subprocess

import pytest
import yaml
from check_commits import main as check_range
from check_manifest import main as check_manifest
from test_starter import VALID


@pytest.mark.parametrize(
    ("profile", "floor"), [("sandbox", 0), ("production", 80), ("consequential", 80)]
)
def test_manifest_outputs_the_profile_floor(tmp_path, capsys, profile, floor):
    manifest = tmp_path / "project.yml"
    manifest.write_text(yaml.safe_dump({**VALID, "profile": profile}))
    assert check_manifest(str(manifest)) == 0
    assert capsys.readouterr().out.splitlines() == [
        f"profile={profile}",
        f"coverage_min={floor}",
        "linear_key=SOS",
    ]
    assert check_manifest(str(manifest), coverage_only=True) == 0
    assert capsys.readouterr().out.strip() == str(floor)


@pytest.mark.parametrize("contents", ["", "owners: [", "expiry: 2027-02-30", "profile: invalid"])
def test_bad_manifest_cannot_emit_ci_outputs(tmp_path, capsys, contents):
    manifest = tmp_path / "project.yml"
    manifest.write_text(contents)
    assert check_manifest(str(manifest)) == 1
    output = capsys.readouterr()
    assert not output.out and output.err


def test_duplicate_profile_cannot_silently_replace_the_coverage_floor(tmp_path, capsys):
    manifest = tmp_path / "project.yml"
    manifest.write_text(yaml.safe_dump({**VALID, "profile": "production"}) + "profile: sandbox\n")
    assert check_manifest(str(manifest)) == 1
    output = capsys.readouterr()
    assert not output.out and output.err


def test_commit_gate_checks_the_whole_pr_range(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)

    def git(*args):
        """Run Git in the disposable repo and return its output, raising on failure."""
        return subprocess.run(  # noqa: S603
            ["git", *args],  # noqa: S607
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    git("init", "-q")
    git("config", "user.name", "Contributor")
    git("config", "user.email", "contributor@example.org")
    git("config", "commit.gpgsign", "false")
    git("commit", "--allow-empty", "-qm", "Base predates the issue rule")
    base = git("rev-parse", "HEAD")
    git("commit", "--allow-empty", "-qm", "SOS-12 Add parser\n\nContext\x1econtinues")
    assert check_range(base, "HEAD", "SOS") == 0
    git("config", "user.name", "sos-agents-app[bot]")
    git(
        "commit",
        "--allow-empty",
        "--author",
        "Contributor <contributor@example.org>",
        "-qm",
        "SOS-12 Work",
    )
    invalid = git("rev-parse", "HEAD")
    git("commit", "--allow-empty", "-qm", "SOS-12 Finalize\n\nAgent: builder")
    assert check_range(base, "HEAD", "SOS") == 1
    assert invalid[:10] in capsys.readouterr().out


def test_commit_gate_skips_merge_commits_from_updating_a_branch(tmp_path, monkeypatch):
    """The ruleset makes a branch catch up with main; that merge has no issue of its own."""
    monkeypatch.chdir(tmp_path)

    def git(*args):
        """Run Git in the disposable repo and return its output, raising on failure."""
        return subprocess.run(  # noqa: S603
            ["git", "-c", "commit.gpgsign=false", *args],  # noqa: S607
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()

    git("init", "-q", "-b", "main")
    git("config", "user.name", "Contributor")
    git("config", "user.email", "contributor@example.org")
    git("commit", "--allow-empty", "-qm", "Base predates the issue rule")
    base = git("rev-parse", "HEAD")
    git("checkout", "-qb", "work")
    git("commit", "--allow-empty", "-qm", "SOS-12 Add parser")
    git("checkout", "-q", "main")
    git("commit", "--allow-empty", "-qm", "SOS-13 Unrelated change on main")
    git("checkout", "-q", "work")
    git("merge", "-q", "--no-ff", "-m", "Merge branch 'main' into work", "main")
    assert check_range(base, "HEAD", "SOS") == 0
    git("commit", "--allow-empty", "-qm", "No issue named")
    assert check_range(base, "HEAD", "SOS") == 1
