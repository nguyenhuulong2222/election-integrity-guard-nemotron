## What changes

<!-- One or two sentences. -->

## Linked issue (required)

Closes #

<!-- The integrity checker BLOCKs any MR that does not reference an issue. -->

## Type of change

- [ ] Results update (`results/`)
- [ ] Voter information or links (`public/`)
- [ ] Policy, allowlist or CSP (`config/`, `<meta>` CSP)
- [ ] Automation (`.gitlab-ci.yml`, `checker/`, `.gitlab/`)

## Supervised release

- The Duo integrity flow reviews this MR **after** the pipeline finishes. It comments and labels the MR, and opens an issue for each BLOCK finding.
- The agent cannot merge, approve or deploy.
- A human approver (a code owner for protected paths) decides whether this ships.

- [ ] I read the integrity review comment
- [ ] Every `integrity::warn` finding is explained below

### Warning explanations

