# RRC-ACT Power Calculation v1.1

This calculation is fixed before confirmatory outcome inspection. It is a conservative planning calculation for the primary relation-specific versus task-only contrast in the persistent-memory, intact-self-model cell.

- Two-sided alpha: `0.05`
- Minimum meaningful standardized effect: `d = 0.50`
- Primary arm size: `n = 64` valid agent instances per A level (32 per model family)
- Independent unit: agent instance
- Approximation: two-sample normal approximation; no credit for baseline adjustment, blocking, or repeated sessions

For equal arms, the noncentrality approximation is:

`delta = d * sqrt(n / 2) = 0.50 * sqrt(64 / 2) = 2.828427`

Using a two-sided normal critical value `z_(1-alpha/2) = 1.959964`:

`power = Phi(-z - delta) + 1 - Phi(z - delta) = 0.807430`

The planned value is therefore approximately **0.807 power**, slightly above the 0.80 target. Exact blocked randomization power may differ; it must be reported from the frozen analysis code if calculated. No outcome-based re-estimation or pilot-based direction setting is permitted.

A primary arm with fewer than 64 valid agents is labeled underpowered or inconclusive for a null interpretation, even if its p-value is above 0.05.
