"""Check pull request commits (CS-04.2, CS-04.4).

Every commit message names its Linear issue. Commits by the sos-agents App
also carry an "Agent:" trailer naming the agent that acted.
"""

import re
import subprocess
import sys

AGENT_LOGIN = "sos-agents[bot]"


def list_commits(base: str, head: str) -> list[tuple[str, str, str]]:
    """Return (sha, author name, full message) for commits in base..head."""
    out = subprocess.run(
        ["git", "log", "--format=%H%x1f%an%x1f%B%x1e", f"{base}..{head}"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    commits = []
    for record in out.split("\x1e"):
        record = record.strip()
        if record:
            sha, author, message = record.split("\x1f", 2)
            commits.append((sha, author, message))
    return commits


def check_commit(author: str, message: str, team_key: str) -> list[str]:
    """Return the problems with one commit; empty means it passes."""
    problems = []
    if not re.search(rf"\b{re.escape(team_key)}-\d+\b", message):
        problems.append(f"no Linear issue ({team_key}-123) in the message")
    if author == AGENT_LOGIN and not re.search(r"^Agent: \S+", message, re.MULTILINE):
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
    sys.exit(main(*sys.argv[1:4]))
