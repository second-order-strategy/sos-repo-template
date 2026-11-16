# Security policy

**Classification:** Public

## Reporting a vulnerability

Please report security issues privately through GitHub's **Report a vulnerability** button on this repository's Security tab. Do not open a public issue.

You can expect an acknowledgement within 3 business days. Findings are handled under the severity table in Coding Standard SOS-STD-001, CS-06.3: critical and high findings introduced by a change block merge. Existing critical findings require immediate containment. Existing critical and high findings have a seven-day fix window.

## What this repository enforces

- Secret scanning of the full history on every pull request, by gitleaks in CI (CS-06.1)
- Dependency scanning and static analysis on every pull request (CS-06.2)
- Signed commits on the default branch (CS-06.5)
- Third-party GitHub Actions pinned to a commit SHA (CS-06.6)
