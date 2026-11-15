# Threat model

**Classification:** Public · Required for Production and Consequential (CS-06.8, EOS-DES-01)

| Asset | Who could misuse it | How | Control | Status |
| --- | --- | --- | --- | --- |
| Source and CI | A compromised agent token | Edits CI to pass bad code | Workflow files are code-owner protected; sos-agents has no workflow permission; required check comes only from GitHub Actions | In place |
| | | | | |

## Trust boundaries

## AI overlay (if applicable)

Prompt injection, unauthorized tool use, excessive permissions (EOS-AGT-03).
