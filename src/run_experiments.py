"""Run the numerical experiments reported in the AAA-WSN analysis paper.

The script keeps the experiment settings in one place and writes the numerical
results to CSV files. The same files can then be used to create the tables and
figures included in the manuscript.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.security_models import (
    boundary_probability,
    exhaustive_state_check,
    ge_metrics,
    m_tradeoff,
    n_boundary_star,
    rejection_probability,
    robust_n_star,
)

DEFAULT_SEED = 20260904
DEFAULT_MC_SAMPLES = 500_000


def _monte_carlo_rejection_with_rng(K: int, N: int, p: float, samples: int, rng) -> float:
    processed_before_n_losses = rng.negative_binomial(N, p, size=samples)
    boundary_time = N + processed_before_n_losses
    wait_for_processed_message = rng.geometric(1.0 - p, size=samples)
    rejection_time = boundary_time + wait_for_processed_message
    return float(np.mean(rejection_time <= K))


def build_results(
    mc_samples: int = DEFAULT_MC_SAMPLES,
    seed: int = DEFAULT_SEED,
    exhaustive_max_N: int = 8,
    exhaustive_max_K: int = 12,
):
    """Calculate all numerical results used by the validation section."""

    rng = np.random.default_rng(seed)

    mc_configs = [
        (100, 0.01, 4),
        (100, 0.02, 6),
        (100, 0.05, 10),
        (200, 0.05, 14),
        (500, 0.01, 9),
        (500, 0.02, 15),
        (500, 0.05, 35),
        (1000, 0.01, 18),
        (1000, 0.02, 30),
        (1000, 0.05, 65),
    ]

    mc_rows = []
    for K, p, N in mc_configs:
        exact = rejection_probability(K, N, p)
        simulated = _monte_carlo_rejection_with_rng(K, N, p, mc_samples, rng)
        mc_rows.append(
            {
                "K": K,
                "p": p,
                "N": N,
                "Exact_PR": exact,
                "MonteCarlo_PR": simulated,
                "AbsError": abs(simulated - exact),
            }
        )
    mc_df = pd.DataFrame(mc_rows)

    eps = 1e-3
    n_rows = []
    for K in (100, 1000, 10000):
        for p in (0.01, 0.02, 0.05, 0.10):
            N = n_boundary_star(K, p, eps)
            n_rows.append(
                {
                    "K": K,
                    "p": p,
                    "epsilon": eps,
                    "N_star": N,
                    "BoundaryProb": boundary_probability(K, N, p),
                    "ExpectedHashes": N + 3,
                    "RelativeNominal": (N + 3) / 4,
                }
            )
    n_df = pd.DataFrame(n_rows)

    active_rows = []
    for B in (0, 2, 5):
        active_rows.append(
            {
                "K": 1000,
                "p": 0.01,
                "epsilon": eps,
                "B": B,
                "N_robust": robust_n_star(1000, 0.01, eps, B),
            }
        )
    active_df = pd.DataFrame(active_rows)

    ge_rows = []
    channel_cases = {
        "Short-burst": (0.02, 0.20, 0.005, 0.45),
        "Long-burst": (0.005, 0.05, 0.005, 0.45),
    }
    for name, parameters in channel_cases.items():
        for N in (5, 8):
            p_bar, p_rejection, mean_attempts = ge_metrics(N, *parameters, K=1000)
            ge_rows.append(
                {
                    "Channel": name,
                    "N": N,
                    "p_bar": p_bar,
                    "P_rej_K1000": p_rejection,
                    "MeanAttemptsToRejection": mean_attempts,
                }
            )
    ge_df = pd.DataFrame(ge_rows)

    m_rows = []
    for M in (1, 2, 4, 9, 19):
        row = m_tradeoff(M)
        m_rows.append(
            {
                "M": M,
                "AvgBits": row["average_bits"],
                "SavingFraction": row["saving_fraction"],
                "LinkabilityLowerBound": row["linkability_lower_bound"],
            }
        )
    m_df = pd.DataFrame(m_rows)

    exhaustive = exhaustive_state_check(exhaustive_max_N, exhaustive_max_K)
    rmse = math.sqrt(float(np.mean((mc_df["MonteCarlo_PR"] - mc_df["Exact_PR"]) ** 2)))
    mae = float(np.mean(np.abs(mc_df["MonteCarlo_PR"] - mc_df["Exact_PR"])))

    summary = {
        "monte_carlo_samples_per_configuration": mc_samples,
        "seed": seed,
        "rmse": rmse,
        "mae": mae,
        "exhaustive_checked_traces": exhaustive["checked_traces"],
        "exhaustive_mismatches": exhaustive["mismatches"],
        "exhaustive_max_N": exhaustive_max_N,
        "exhaustive_max_K": exhaustive_max_K,
    }

    return {
        "monte_carlo_validation": mc_df,
        "n_design": n_df,
        "active_suppression": active_df,
        "gilbert_elliott": ge_df,
        "m_tradeoff": m_df,
        "summary": summary,
    }


def write_results(bundle, output_dir: Path) -> None:
    """Write experiment tables and the validation summary to disk."""

    output_dir.mkdir(parents=True, exist_ok=True)

    for name in (
        "monte_carlo_validation",
        "n_design",
        "active_suppression",
        "gilbert_elliott",
        "m_tradeoff",
    ):
        bundle[name].to_csv(output_dir / f"{name}.csv", index=False)

    summary = bundle["summary"]
    with open(output_dir / "validation_summary.json", "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    with open(output_dir / "validation_summary.txt", "w", encoding="utf-8") as handle:
        handle.write(f"Monte Carlo samples/configuration: {summary['monte_carlo_samples_per_configuration']}\n")
        handle.write(f"Seed: {summary['seed']}\n")
        handle.write(f"RMSE: {summary['rmse']:.12g}\n")
        handle.write(f"MAE: {summary['mae']:.12g}\n")
        handle.write(f"Exhaustive bounded trace cases checked: {summary['exhaustive_checked_traces']}\n")
        handle.write(f"Exhaustive mismatches: {summary['exhaustive_mismatches']}\n")
        handle.write(
            f"Exhaustive bounds: N<={summary['exhaustive_max_N']}, K<={summary['exhaustive_max_K']}\n"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AAA-WSN numerical validation experiments.")
    parser.add_argument("--mc-samples", type=int, default=DEFAULT_MC_SAMPLES)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()

    bundle = build_results(mc_samples=args.mc_samples, seed=args.seed)
    write_results(bundle, args.output)

    summary = bundle["summary"]
    print(f"RMSE={summary['rmse']:.9g}")
    print(f"MAE={summary['mae']:.9g}")
    print(f"Exhaustive cases={summary['exhaustive_checked_traces']}")
    print(f"Exhaustive mismatches={summary['exhaustive_mismatches']}")


if __name__ == "__main__":
    main()
