# Evidence index

**Classification:** Public

Evidence comes from the run, never from the author (EOS-EVD-02, CS-05.5).

- **Every pull request:** the `ci` workflow uploads `ci-evidence.json` (commit, profile, each check's result) and test reports as run artifacts.
- **Every release tag:** the `release` workflow attaches `sbom.spdx.json` and `release-evidence.json` to the GitHub Release, which doesn't expire.
- **Owner decisions (G1 to G5):** recorded in Linear, linked from the release.

List each release here with its links.
