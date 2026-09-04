import math

import numpy as np

from src.security_models import (
    boundary_probability,
    expected_boundary_attempts,
    expected_rejection_attempts,
    ge_metrics,
    m_tradeoff,
    n_boundary_star,
    rejection_probability,
    robust_boundary_probability,
    robust_n_star,
    synchronization_distance,
)


def test_synchronization_distance_is_cumulative():
    trace = [1, 0, 1, 0, 1]
    assert synchronization_distance(trace) == 3


def test_boundary_design_value_matches_paper_case():
    assert n_boundary_star(K=1000, p=0.01, eps=1e-3) == 22


def test_expected_attempts_separates_boundary_and_actual_rejection():
    N = 5
    p = 0.05
    assert expected_boundary_attempts(N, p) == 100.0
    expected = 100.0 + 1.0 / 0.95
    assert math.isclose(expected_rejection_attempts(N, p), expected, rel_tol=1e-12)


def test_rejection_probability_is_not_larger_than_boundary_probability():
    K, N, p = 1000, 22, 0.01
    assert rejection_probability(K, N, p) <= boundary_probability(K, N, p)


def test_active_suppression_design_values():
    assert robust_n_star(1000, 0.01, 1e-3, 0) == 22
    assert robust_n_star(1000, 0.01, 1e-3, 2) == 24
    assert robust_n_star(1000, 0.01, 1e-3, 5) == 27


def test_active_suppression_boundary_is_one_when_budget_reaches_N():
    assert robust_boundary_probability(1000, 5, 0.01, 5) == 1.0


def test_m_tradeoff_exact_relation():
    row = m_tradeoff(9)
    assert math.isclose(row["average_bits"], 1468.8, rel_tol=1e-12)
    assert math.isclose(row["saving_fraction"], 0.9, rel_tol=1e-12)
    assert math.isclose(row["linkability_lower_bound"], 0.8, rel_tol=1e-12)
    assert math.isclose(row["linkability_lower_bound"], 2 * row["saving_fraction"] - 1, rel_tol=1e-12)


def test_gilbert_elliott_preserves_selected_average_loss_rate():
    pbar, p_rej, mean = ge_metrics(
        N=5,
        a=0.02,
        b=0.20,
        eG=0.005,
        eB=0.45,
        K=1000,
    )
    assert math.isclose(pbar, 0.045454545454545456, rel_tol=1e-12)
    assert 0.0 <= p_rej <= 1.0
    assert mean > 0.0


def test_small_case_rejection_probability_matches_direct_enumeration():
    K, N, p = 5, 2, 0.2
    exact = rejection_probability(K, N, p)

    total = 0.0
    for mask in range(1 << K):
        trace = [(mask >> i) & 1 for i in range(K)]
        probability = np.prod([p if x else (1 - p) for x in trace])
        D = 0
        rejected = False
        for x in trace:
            if D == N and x == 0:
                rejected = True
                break
            if x == 1:
                D = min(N, D + 1)
        if rejected:
            total += probability

    assert math.isclose(exact, total, rel_tol=1e-12, abs_tol=1e-12)


def test_exhaustive_state_check_counts_all_bounded_traces():
    from src.security_models import exhaustive_state_check

    result = exhaustive_state_check(max_N=3, max_K=5)
    assert result["checked_traces"] == 186
    assert result["mismatches"] == 0


def test_monte_carlo_rejection_is_close_to_exact_small_case():
    from src.security_models import monte_carlo_rejection

    K, N, p = 100, 4, 0.01
    exact = rejection_probability(K, N, p)
    sim = monte_carlo_rejection(K, N, p, samples=200_000, seed=7)
    assert abs(sim - exact) < 0.0015
