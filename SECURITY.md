# Security Policy

## Reporting

For security issues in the experimental infrastructure or documentation:

1. Do **not** open a public issue.
2. Email: 263311487@qq.com
3. Response within 72 hours.

## Scope

- `experiments/rrc_act/` — experiment runner, scorer, allocation logic
- `tutorials/` — tutorial scripts

## Notes

- The synthetic replay infrastructure does not call any external API by default.
- No credentials or model API keys are stored in this repository.
- If you discover that the tooling could silently make real model calls (bypassing the synthetic-only gate), that is in scope.
