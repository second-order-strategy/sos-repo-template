# Threat model

**Classification:** Public · Required for Production and Consequential (CS-06.8, EOS-DES-01)

| Asset | Who could misuse it | How | Control | Status |
| --- | --- | --- | --- | --- |
| Source and CI | A compromised agent token | Edits CI to pass bad code | Workflow files are code-owner protected; sos-agents-app has no workflow permission; required check comes only from GitHub Actions | Verified for this template on 2026-11-16. Recheck in each new repository. |
| Source and CI | Another installed GitHub App with workflow write access (Codex Connector, Linear) | Pushes a branch that edits CI | Workflow files are code-owner protected, so the edit cannot merge without the owner | In place. App permissions are not yet recorded in the Agent Access register. |
| | | | | |

## Trust boundaries

## AI overlay (if applicable)

Prompt injection, unauthorized tool use, excessive permissions (EOS-AGT-03).
