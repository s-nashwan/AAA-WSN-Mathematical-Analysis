from src.run_experiments import build_results


def test_build_results_contains_all_paper_tables():
    bundle = build_results(mc_samples=5_000, seed=11, exhaustive_max_N=3, exhaustive_max_K=5)

    assert set(bundle) == {
        "monte_carlo_validation",
        "n_design",
        "active_suppression",
        "gilbert_elliott",
        "m_tradeoff",
        "summary",
    }
    assert len(bundle["n_design"]) == 12
    assert list(bundle["active_suppression"]["N_robust"]) == [22, 24, 27]
    assert len(bundle["gilbert_elliott"]) == 4
    assert len(bundle["m_tradeoff"]) == 5
    assert bundle["summary"]["exhaustive_mismatches"] == 0
    assert bundle["summary"]["exhaustive_checked_traces"] == 186
