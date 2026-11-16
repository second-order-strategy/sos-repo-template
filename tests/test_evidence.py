"""Run the embedded workflow steps with local files and no GitHub credentials."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest
import yaml

WORKFLOWS = Path(__file__).resolve().parents[1] / ".github" / "workflows"


def run_step(workflow, job, name, directory, **env):
    """Execute the named shell step in an isolated directory and return its status and output."""
    jobs = yaml.safe_load((WORKFLOWS / workflow).read_text())["jobs"]
    command = next(step["run"] for step in jobs[job]["steps"] if step.get("name") == name)
    return subprocess.run(  # noqa: S603
        ["bash", "-eu", "-o", "pipefail", "-c", command],  # noqa: S607
        cwd=directory,
        env={"PATH": os.environ["PATH"], **env},
        capture_output=True,
        text=True,
        check=False,
    )


def test_pr_evidence_identifies_the_revision_tested(tmp_path):
    result = run_step(
        "ci.yml",
        "evidence",
        "Write the evidence record from this run",
        tmp_path,
        RESULTS=json.dumps({"test": {"result": "failure"}}),
        PROFILE="production",
        GITHUB_REPOSITORY="org/project",
        GITHUB_SHA="merge",
        PR_HEAD="head",
        RUN_URL="run/1",
    )
    assert result.returncode == 0, result.stderr
    record = json.loads((tmp_path / "evidence/ci-evidence.json").read_text())
    assert (record["commit"], record["pr_head"]) == ("merge", "head")
    assert record["checks"]["test"] == "failed"


@pytest.mark.parametrize("revision", ["tagged", "different"])
def test_release_carries_verification_for_its_own_revision(tmp_path, revision):
    ci = {"repository": "org/project", "commit": revision, "checks": {"test": "passed"}}
    verified = tmp_path / "verified-ci"
    verified.mkdir()
    (verified / "ci-evidence.json").write_text(json.dumps(ci))
    sbom = b'{"spdxVersion":"SPDX-2.3"}'
    (tmp_path / "sbom.spdx.json").write_bytes(sbom)
    result = run_step(
        "release.yml",
        "release-evidence",
        "Write release evidence record",
        tmp_path,
        RUNNER_TEMP=str(tmp_path),
        GITHUB_REPOSITORY="org/project",
        GITHUB_SHA="tagged",
        TAG="v1",
        RUN_URL="run/2",
    )
    output = tmp_path / "release-evidence.json"
    if revision != "tagged":
        assert result.returncode != 0
        assert not output.exists()
        return
    assert result.returncode == 0, result.stderr
    record = json.loads(output.read_text())
    assert record["verification"] == ci
    assert record["sbom_sha256"] == hashlib.sha256(sbom).hexdigest()


@pytest.mark.parametrize("status", ["absent", "draft", "published"])
def test_workflow_only_writes_draft_releases(tmp_path, status):
    gh = tmp_path / "gh"
    gh.write_text(
        "#!/bin/sh\n"
        'echo "$*" >> calls\n'
        'if [ "$2" = view ]; then\n'
        '  case "$STATUS" in absent) exit 1;; draft) echo true;; published) echo false;; esac\n'
        "fi\n"
    )
    gh.chmod(0o700)
    result = run_step(
        "release.yml",
        "release-evidence",
        "Attach SBOM and evidence to the release",
        tmp_path,
        PATH=f"{tmp_path}:{os.environ['PATH']}",
        TAG="v1",
        STATUS=status,
    )
    calls = (tmp_path / "calls").read_text().splitlines()
    if status == "published":
        assert result.returncode != 0
        assert len(calls) == 1
    elif status == "draft":
        assert result.returncode == 0 and calls[-1].startswith("release upload v1 ")
    else:
        assert result.returncode == 0 and calls[-1].startswith("release create v1 ")
        assert "--draft" in calls[-1]
