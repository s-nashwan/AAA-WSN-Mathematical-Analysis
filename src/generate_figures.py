"""Generate figures directly from the numerical results.

The figures are produced from the same CSV tables created by run_experiments.py.
This keeps the numerical evidence and the visual presentation connected to the
same experiment outputs.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: Path) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_all_figures(bundle, output_dir: Path):
    """Generate the main validation figures and return their paths."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    n_df = bundle["n_design"]
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    for p_value, group in n_df.groupby("p"):
        ordered = group.sort_values("K")
        ax.plot(ordered["K"], ordered["N_star"], marker="o", label=f"p={p_value:g}")
    ax.set_xscale("log")
    ax.set_xlabel("Authentication horizon K")
    ax.set_ylabel("Required synchronization value N*")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    paths.append(_save(fig, output_dir / "n_vs_horizon.png"))

    ge_df = bundle["gilbert_elliott"]
    pivot = ge_df.pivot(index="N", columns="Channel", values="P_rej_K1000")
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    pivot.plot(kind="bar", ax=ax)
    ax.set_xlabel("Synchronization value N")
    ax.set_ylabel("Rejection probability for K=1000")
    ax.legend(title="Channel", frameon=False)
    ax.grid(True, axis="y", alpha=0.25)
    paths.append(_save(fig, output_dir / "bursty_loss_comparison.png"))

    active_df = bundle["active_suppression"].sort_values("B")
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.plot(active_df["B"], active_df["N_robust"], marker="o")
    ax.set_xlabel("Suppression budget B")
    ax.set_ylabel("Required robust value N*rob")
    ax.grid(True, alpha=0.25)
    paths.append(_save(fig, output_dir / "active_suppression_design.png"))

    m_df = bundle["m_tradeoff"].sort_values("M")
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.plot(m_df["M"], 100 * m_df["SavingFraction"], marker="o", label="Communication saving")
    ax.plot(
        m_df["M"],
        100 * m_df["LinkabilityLowerBound"],
        marker="s",
        label="Linkability lower bound",
    )
    ax.set_xlabel("Subsequent authentication parameter M")
    ax.set_ylabel("Percentage (%)")
    ax.legend(frameon=False)
    ax.grid(True, alpha=0.25)
    paths.append(_save(fig, output_dir / "m_tradeoff.png"))

    return paths


def load_results(results_dir: Path):
    """Load the CSV tables required for figure generation."""

    results_dir = Path(results_dir)
    return {
        "n_design": pd.read_csv(results_dir / "n_design.csv"),
        "gilbert_elliott": pd.read_csv(results_dir / "gilbert_elliott.csv"),
        "active_suppression": pd.read_csv(results_dir / "active_suppression.csv"),
        "m_tradeoff": pd.read_csv(results_dir / "m_tradeoff.csv"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate AAA-WSN validation figures from result CSV files.")
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--output", type=Path, default=Path("figures"))
    args = parser.parse_args()

    bundle = load_results(args.results)
    paths = generate_all_figures(bundle, args.output)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
