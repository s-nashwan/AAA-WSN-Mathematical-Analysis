from src.generate_figures import generate_all_figures
from src.run_experiments import build_results


def test_generate_all_figures_creates_expected_files(tmp_path):
    bundle = build_results(mc_samples=2_000, seed=3, exhaustive_max_N=2, exhaustive_max_K=4)
    paths = generate_all_figures(bundle, tmp_path)

    assert {p.name for p in paths} == {
        "n_vs_horizon.png",
        "bursty_loss_comparison.png",
        "active_suppression_design.png",
        "m_tradeoff.png",
    }
    assert all(p.exists() and p.stat().st_size > 0 for p in paths)
