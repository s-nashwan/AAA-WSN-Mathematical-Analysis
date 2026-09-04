# Main Numerical Results

This file summarizes the main numerical outputs reproduced by the repository. The mathematical derivations remain in the paper, while the code is used to verify the numerical values and the bounded state behavior.

## Independent-loss validation

The Monte Carlo experiment uses 500,000 trajectories for each selected configuration and the fixed seed 20260904. Across the ten validation configurations, the current reproducibility run gives:

- RMSE: `9.22417029484e-05`
- MAE: `8.20037526817e-05`

The complete values are stored in `results/monte_carlo_validation.csv`.

## Exhaustive authentication-state analysis

All binary processed/unprocessed traces are checked for `N <= 8` and `K <= 12`. The current run checks 65,520 bounded traces and reports zero mismatches. Therefore, the executable state evolution is consistent with the cumulative synchronization invariant within the selected exhaustive bounds.

The complete summary is stored in `results/validation_summary.json` and `results/validation_summary.txt`.

## Reliability-driven selection of N

The file `results/n_design.csv` reports the minimum value of `N` required to keep the synchronization-boundary probability below the selected value of `epsilon = 10^-3`. It also reports the corresponding expected sensor-node hash operations and the cost relative to the nominal four-hash sensor computation.

For example, when `K = 1000` and `p = 0.01`, the required value is `N = 22`. The corresponding expected sensor-node computation is 25 hash operations, which is 6.25 times the nominal four-hash cost.

## Bursty message losses

The Gilbert-Elliott results are stored in `results/gilbert_elliott.csv`. Two channels with approximately the same average loss probability are evaluated with different burst characteristics. The purpose is to show that the average loss probability alone does not completely describe the synchronization behavior.

## Bounded active suppression

The file `results/active_suppression.csv` reports the robust value of `N` when a bounded number of `M2` messages can be deliberately suppressed. For `K = 1000`, `p = 0.01`, and `epsilon = 10^-3`, the required values are 22, 24, and 27 for suppression budgets `B = 0`, `2`, and `5`, respectively.

## Subsequent-authentication parameter M

The file `results/m_tradeoff.csv` reports the average communication cost, normalized communication saving, and session-linkability lower bound for representative values of `M`. These values reproduce the mathematical tradeoff developed in Section 6 of the paper.

The numerical files are intentionally kept separate from the analytical derivations. Therefore, the repository can be used to reproduce the reported results without replacing the mathematical argument presented in the manuscript.
