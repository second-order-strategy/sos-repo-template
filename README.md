# Project name

<!-- Replace this README when you create a repository from the template. Keep every heading. -->

**Profile:** Sandbox · **Classification:** Public · **Linear:** AI-000 · **Standard:** SOS-EOS-001 v1.0, SOS-STD-001 v1.2

## What this is

One or two sentences: what it does and for whom.

## Why it exists

The business goal it moves, and how we'll know (EOS-DSC-01).

## Sandbox purpose and expiry

What this experiment should settle, and its expiry date (also in `sos-project.yml`). Main risks for a Sandbox go here (CS-06.8).

## Install, run and test

```
make install
make test
```

A new team should be able to do this without contacting the author (Handoff Test, CS-03.4).

## Layout

| Path | Holds |
| --- | --- |
| `src/` | The code |
| `tests/` | Unit, integration and end-to-end tests |
| `docs/` | Threat model, decision records, evidence index |
| `scripts/` | CI checks for the manifest and commits |
| `.github/` | CI workflows, CODEOWNERS, templates |
| `sos-project.yml` | Profile, owners, Linear issue |

## Records

- Linear issue: AI-000
- Threat model: `docs/threat-model.md`
- Decisions: `docs/decisions/`
- Evidence: produced by CI on every run; releases carry an SBOM and evidence file (`docs/evidence/README.md`)

## Licence

Code: Apache-2.0 (`LICENSE`). Documentation: CC BY 4.0 (`LICENSE-docs`).
