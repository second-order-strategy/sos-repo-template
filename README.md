# Second Order Strategy repository template

<!-- Replace this README when you create a repository from the template. Keep every heading. -->

**Profile:** Sandbox · **Classification:** Public · **Standard:** SOS-EOS-001 v1.0, SOS-STD-001 v1.2

## What this is

Use this GitHub template to start a project with a Python package, tests, a project manifest and a CI gate. The starter function gives a new team something small to run before replacing it with project code.

## Why it exists

A new team should be able to clone a repository, run its code and verify the same checks CI uses (CS-03.4).

## Sandbox purpose and expiry

This Sandbox exercises the starter and its CI controls. Its current expiry is **2027-02-14**. The main risks are inheriting example governance records and assuming GitHub settings copy with the files.

When creating a project, register it in Linear. Replace the example issue, profile, overlays, expiry and owners in `sos-project.yml`. Update this README, the package metadata, CODEOWNERS and the threat model for the new project. Verify the destination's ruleset, required `ci-gate`, code-owner review, signed commits and private vulnerability reporting.

## Install, run and test

From the repository root, use Python 3.12 or later, Git and Make. CI uses Python 3.12. On macOS or Linux:

```sh
python3.12 -m venv .venv
. .venv/bin/activate
make install
python -c 'from sos_app import describe_project; print(describe_project("Triage"))'
python scripts/check_manifest.py sos-project.yml
make lint test coverage
```

`make coverage` and CI get the coverage floor from the manifest. It is 0% for Sandbox and 80% for Production and Consequential. To exercise the latter locally, run `make coverage COVERAGE_MIN=80`.

## Layout

| Path | Holds |
| --- | --- |
| `src/` | The starter package |
| `tests/` | Tests of the package and CI checks |
| `docs/` | Threat model, decision records and evidence index |
| `scripts/` | CI checks for the manifest and commits |
| `.github/` | CI and release workflows, CODEOWNERS and pull request template |
| `sos-project.yml` | Project profile, owners and Linear registration |

## Records

- The [project manifest](sos-project.yml) names the registration issue. `SOS-25` registered this template; a new project replaces it with its own.
- [Threat model](docs/threat-model.md) and [decision records](docs/decisions/)
- [CI and release evidence](docs/evidence/README.md)

## Licence

[Apache-2.0 for code](LICENSE) and [CC BY 4.0 for documentation](LICENSE-docs).
