"""Validate sos-project.yml and print CI outputs (EOS-PRF-01, EOS-PRF-02, CS-05.2)."""

import argparse
import datetime
import re
import sys

import yaml

PROFILES = {"sandbox": 0, "production": 80, "consequential": 80}
ROLES = ("outcome", "engineering", "release", "operational")
STANDARD = "SOS-EOS-001 v1.0"


class ManifestLoader(yaml.SafeLoader):
    """Reject duplicate field names before PyYAML silently replaces their values."""

    def construct_mapping(self, node, deep=False):
        """Check explicit field names while preserving normal YAML merge-key handling."""
        names = set()
        for key_node, _ in node.value:
            if key_node.tag == "tag:yaml.org,2002:str":
                if key_node.value in names:
                    raise yaml.constructor.ConstructorError(
                        None, None, "duplicate manifest field", key_node.start_mark
                    )
                names.add(key_node.value)
        return super().construct_mapping(node, deep=deep)


def validate_manifest(data: object) -> list[str]:
    """Return field errors for a parsed manifest, or an empty list when valid."""
    if not isinstance(data, dict):
        return ["manifest must be a mapping"]
    problems = []
    if data.get("standard") != STANDARD:
        problems.append(f"standard must be {STANDARD}")
    profile = data.get("profile")
    if not isinstance(profile, str) or profile not in PROFILES:
        problems.append(f"profile must be one of {sorted(PROFILES)}")
    if data.get("classification") not in ("public", "internal"):
        problems.append("classification must be public or internal")
    overlays = data.get("overlays")
    if not isinstance(overlays, list) or any(item not in ("ai", "data") for item in overlays):
        problems.append("overlays must be a list of ai or data")
    elif len(overlays) != len(set(overlays)):
        problems.append("overlays must not repeat")
    linear = data.get("linear")
    if not isinstance(linear, dict):
        problems.append("linear must be a mapping")
    else:
        key, issue = linear.get("team_key"), linear.get("issue")
        if not isinstance(key, str) or not re.fullmatch(r"[A-Z][A-Z0-9]*", key):
            problems.append("linear.team_key must be an uppercase team identifier")
        elif not isinstance(issue, str) or not re.fullmatch(rf"{key}-[0-9]+", issue):
            problems.append("linear.issue must be an issue identifier for linear.team_key")
    owners = data.get("owners")
    if not isinstance(owners, dict):
        problems.append("owners must be a mapping")
    else:
        for role in ROLES:
            owner = owners.get(role)
            if not isinstance(owner, str) or not owner.strip():
                problems.append(f"owners.{role} must name an owner")
    if profile == "sandbox":
        expiry = data.get("expiry")
        if isinstance(expiry, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", expiry):
            try:
                expiry = datetime.date.fromisoformat(expiry)
            except ValueError:
                pass  # Report the same field error for all malformed dates.
        if not isinstance(expiry, datetime.date) or isinstance(expiry, datetime.datetime):
            problems.append("sandbox needs an expiry date (YYYY-MM-DD)")
        elif expiry < datetime.datetime.now(datetime.UTC).date():
            problems.append(
                f"sandbox expired on {expiry}: promote, extend with a reason, or archive"
            )
    return problems


def main(path: str, *, coverage_only: bool = False) -> int:
    """Write CI outputs only for a valid manifest. Report input errors on stderr."""
    try:
        with open(path, encoding="utf-8") as f:
            data = yaml.load(f, Loader=ManifestLoader)  # noqa: S506 (SafeLoader subclass)
    except (OSError, UnicodeError, ValueError, yaml.YAMLError) as error:
        mark = getattr(error, "problem_mark", None)
        location = f"{path}:{mark.line + 1}" if mark else path
        print(f"{location}: could not read manifest ({type(error).__name__})", file=sys.stderr)
        return 1
    problems = validate_manifest(data)
    if problems:
        for problem in problems:
            print(f"::error file={path}::{problem}", file=sys.stderr)
        return 1
    if coverage_only:
        print(PROFILES[data["profile"]])
        return 0
    print(f"profile={data['profile']}")
    print(f"coverage_min={PROFILES[data['profile']]}")
    print(f"linear_key={data['linear']['team_key']}")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest")
    parser.add_argument("--coverage-min", action="store_true", help="print only the coverage floor")
    args = parser.parse_args()
    sys.exit(main(args.manifest, coverage_only=args.coverage_min))
