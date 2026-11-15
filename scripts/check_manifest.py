"""Validate sos-project.yml and print CI outputs (EOS-PRF-01, EOS-PRF-02, CS-05.2)."""

import datetime
import sys

import yaml

PROFILES = {"sandbox": 0, "production": 80, "consequential": 80}
ROLES = ("outcome", "engineering", "release", "operational")


def validate_manifest(data: dict) -> list[str]:
    """Return a list of problems with the manifest; empty means valid."""
    problems = []
    profile = data.get("profile")
    if profile not in PROFILES:
        problems.append(f"profile must be one of {sorted(PROFILES)}, got {profile!r}")
    if data.get("classification") not in ("public", "internal"):
        problems.append("classification must be public or internal")
    linear = data.get("linear") or {}
    if not linear.get("team_key") or not linear.get("issue"):
        problems.append("linear.team_key and linear.issue are required")
    owners = data.get("owners") or {}
    for role in ROLES:
        if not owners.get(role):
            problems.append(f"owners.{role} is required")
    if profile == "sandbox":
        expiry = data.get("expiry")
        if not isinstance(expiry, datetime.date):
            problems.append("sandbox needs an expiry date (YYYY-MM-DD)")
        elif expiry < datetime.date.today():
            problems.append(
                f"sandbox expired on {expiry}: promote, extend with a reason, or archive"
            )
    return problems


def main(path: str) -> int:
    """Validate the manifest at path and print key=value lines for GITHUB_OUTPUT."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    problems = validate_manifest(data)
    if problems:
        for p in problems:
            print(f"::error file={path}::{p}", file=sys.stderr)
        return 1
    print(f"profile={data['profile']}")
    print(f"coverage_min={PROFILES[data['profile']]}")
    print(f"linear_key={data['linear']['team_key']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
