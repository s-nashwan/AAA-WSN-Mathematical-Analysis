# Relation between the Paper and the Reproducibility Files

The analytical development is presented in the paper. This repository provides the computational part required to verify the numerical results and reproduce the reported experiments.

## Section 3 — Mathematical Synchronization Model

The independent-loss synchronization process is implemented in `src/security_models.py`. The functions `q_matrix`, `rejection_probability`, `boundary_probability`, `expected_boundary_attempts`, and `expected_rejection_attempts` correspond to the state-space and first-passage analysis presented in Section 3.

The function `n_boundary_star` determines the smallest synchronization value `N` that satisfies a predefined boundary probability. The numerical values used in the paper are written to `results/n_design.csv`.

## Section 4 — Sensor-Node Computation Cost

The computation effect is evaluated using the derived relation between `N` and the expected sensor-node hash operations. The selected values are included in `results/n_design.csv` through the columns `ExpectedHashes` and `RelativeNominal`.

The mathematical derivation remains in the paper because the purpose of the code is to reproduce the numerical values rather than repeat the analytical proof.

## Section 5 — Bursty Losses and Active Message Suppression

The Gilbert-Elliott state model is implemented by `ge_metrics`. The selected short-burst and long-burst scenarios are executed by `src/run_experiments.py`, and the results are stored in `results/gilbert_elliott.csv`.

The bounded active-suppression model is implemented through `robust_boundary_probability` and `robust_n_star`. The values reported for `B = 0`, `2`, and `5` are stored in `results/active_suppression.csv`.

## Section 6 — Subsequent Authentication Parameter M

The function `m_tradeoff` evaluates the average communication cost, normalized communication saving, and session-linkability lower bound. The selected values of `M` are stored in `results/m_tradeoff.csv`.

## Section 7 — Numerical and Computational Validation

The Monte Carlo experiment compares the exact rejection probability with simulation for selected values of `K`, `p`, and `N`. The default experiment executes 500,000 trajectories for each configuration using the fixed seed 20260904. The complete output is stored in `results/monte_carlo_validation.csv`.

The bounded exhaustive state analysis checks every binary processed/unprocessed message trace for `N <= 8` and `K <= 12`. The check confirms that the implemented state evolution follows the cumulative synchronization invariant. The number of checked traces and any detected mismatch are reported in `results/validation_summary.json` and `results/validation_summary.txt`.

## Figures

The figures are generated only after the numerical files are created. `src/generate_figures.py` reads the result files and produces the figures in `figures/`. This approach keeps the numerical results and the visual presentation connected to the same computational evidence.
