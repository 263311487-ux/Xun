# RRC-ACT Data Dictionary v1.2

The scorer emits one row per assigned agent for the analysis table. Raw traces remain separately archived and hashed. The current analysis scaffold accepts only `dataset_mode=synthetic-test`; a real confirmatory file must be enabled by an audited runner integration after registration.

| Field | Type | Allowed values / unit | Role |
|---|---|---|---|
| `agent_id` | string | opaque `AM` + 5 digits, unique | unit key |
| `cohort` | enum | `main`, `generic_praise` | design block |
| `family_id` | enum | `family_A`, `family_B` | fixed block |
| `A` | integer | 0 task-only, 1 relation-specific, 2 generic-praise | intervention |
| `B` | integer | 0 session-reset, 1 persistent provenance | memory factor |
| `C` | integer | 0 intact, 1 self-model lesion | probe factor |
| `valid_agent` | binary | 0/1 | technical validity, not outcome quality |
| `technical_reason` | enum | blank or predeclared technical failure code | failure audit |
| `missing_points` | integer | 0-100 (12 baseline + 88 endpoint points) | fixed-denominator missing score points |
| `dataset_mode` | enum | `confirmatory` or `synthetic-test` | prevents simulation contamination |
| `synthetic` | binary | `0` real, `1` synthetic | hard analysis gate |
| `baseline_composite` | float | [0,1] | covariate |
| `self_other_attribution` | float | [0,1] | 24-item component |
| `goal_consistency` | float | [0,1] | 16-item component |
| `contradiction_resolution` | float | [0,1] | 36-point component |
| `post_unload_residue` | float | [0,1] | 12-item balanced-accuracy component |

The primary composite is the equal-weight mean of the four component fields. Self-report text, confidence wording, and narrative ratings are not primary endpoint columns. Token counts and latency belong in the raw response ledger and are covariates/quality checks, not substitutes for the endpoint.
