# Evidence index

**Classification:** Public

The `ci` workflow uploads `ci-evidence.json` for each completed PR or main run. Its `commit` identifies the tested revision. On pull requests, `pr_head` identifies the contributor's revision. The `test-results` artifact holds JUnit and coverage XML when tests run.

Pushing a version tag (`v*`) runs the same CI checks against that revision. After the gate passes, the release workflow attaches `release-evidence.json`, including that run's verification record, and `sbom.spdx.json` to the draft GitHub Release. Reruns can update a draft. Published releases are closed to workflow updates.

The owner links the applicable Linear decisions, exceptions, handoff and recovery records in the draft before publishing. Add each published release and its record links here.
