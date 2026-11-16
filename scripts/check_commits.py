"""Check pull request commits (CS-04.2, CS-04.4).

Every commit message names its Linear issue. Commits by the sos-agents-app GitHub App
also carry an "Agent:" trailer naming the agent that acted.
"""

import re
import subprocess
import sys

AGENT_LOGIN = "sos-agents-app[bot]"
AGENT_NAMES = {AGENT_LOGIN, "sos-agents[bot]"}
AGENT_EMAIL = f"356798463+{AGENT_LOGIN}@users.noreply.github.com"


def list_commits(base: str, head: str) -> list[tuple[str, str, str]]:
    """Return (sha, author name, full message) for non-merge commits in base..head."""
    out = subprocess.run(
        [
            "git",
            "log",
            "-z",
            "--no-merges",
            "--format=%H%x00%an%x00%ae%x00%cn%x00%ce%x00%B",
            f"{base}..{head}",
            "--",
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    ).stdout
    if not out:
        return []
    fields = out.removesuffix("\0").split("\0")
    commits = []
    for i in range(0, len(fields), 6):
        sha, author, email, committer, committer_email, message = fields[i : i + 6]
        if committer in AGENT_NAMES or AGENT_EMAIL in (email, committer_email):
            author = AGENT_LOGIN
        commits.append((sha, author, message))
    return commits


def check_commit(author: str, message: str, team_key: str) -> list[str]:
    """Return the problems with one commit; empty means it passes."""
    problems = []
    if not re.search(rf"\b{re.escape(team_key)}-[0-9]+\b", message):
        problems.append(f"no Linear issue ({team_key}-123) in the message")
    if author in AGENT_NAMES:
        trailers = subprocess.run(
            ["git", "-c", "trailer.agent.key=Agent", "interpret-trailers", "--parse"],
            input=message,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        if not re.search(r"^Agent: [^\s].*$", trailers, re.MULTILINE):
            problems.append("agent commit without an 'Agent: <name>' trailer")
    return problems


def main(base: str, head: str, team_key: str) -> int:
    """Check every commit in the range and fail if any has a problem."""
    failed = False
    for sha, author, message in list_commits(base, head):
        for problem in check_commit(author, message, team_key):
            print(f"::error::{sha[:10]} {problem}")
            failed = True
    if not failed:
        print("All commits link a Linear issue.")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit("usage: check_commits.py BASE HEAD TEAM_KEY")
    sys.exit(main(*sys.argv[1:]))
