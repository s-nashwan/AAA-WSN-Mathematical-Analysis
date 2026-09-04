"""Mathematical models used in the AAA-WSN parameter analysis.

The functions in this module follow the state evolution described in the paper.
The code is kept compact so that each numerical result can be connected directly
with a mathematical expression in the manuscript.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import binom


def _check_probability(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0 and 1.")


def _check_positive_integer(value: int, name: str) -> None:
    if not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer.")


def synchronization_distance(trace) -> int:
    """Return the cumulative number of unprocessed M2 messages in a trace.

    A value of 1 denotes an unprocessed M2 message and 0 denotes a processed
    message. Successful messages do not remove a previously accumulated gap.
    """

    values = list(trace)
    if any(x not in (0, 1) for x in values):
        raise ValueError("The trace must contain only 0 and 1 values.")
    return int(sum(values))


def q_matrix(N: int, p: float) -> np.ndarray:
    """Return the transient matrix for the independent-loss rejection model."""

    _check_positive_integer(N, "N")
    _check_probability(p, "p")
    q = 1.0 - p
    Q = np.zeros((N + 1, N + 1), dtype=float)

    for d in range(N):
        Q[d, d] = q
        Q[d, d + 1] = p

    # At D=N, another unprocessed message keeps the process at the boundary.
    # A processed message causes rejection and therefore leaves the transient set.
    Q[N, N] = p
    return Q


def rejection_probability(K: int, N: int, p: float) -> float:
    """Probability of actual authentication rejection within K attempts."""

    if not isinstance(K, int) or K < 0:
        raise ValueError("K must be a non-negative integer.")
    Q = q_matrix(N, p)
    alpha = np.zeros(N + 1, dtype=float)
    alpha[0] = 1.0
    return float(1.0 - alpha @ np.linalg.matrix_power(Q, K) @ np.ones(N + 1))


def boundary_probability(K: int, N: int, p: float) -> float:
    """Probability that the synchronization distance reaches N within K attempts."""

    if not isinstance(K, int) or K < 0:
        raise ValueError("K must be a non-negative integer.")
    _check_positive_integer(N, "N")
    _check_probability(p, "p")
    return float(binom.sf(N - 1, K, p))


def expected_boundary_attempts(N: int, p: float) -> float:
    """Expected attempts required to accumulate N unprocessed M2 messages."""

    _check_positive_integer(N, "N")
    if not 0.0 < p <= 1.0:
        raise ValueError("p must satisfy 0 < p <= 1.")
    return float(N / p)


def expected_rejection_attempts(N: int, p: float) -> float:
    """Expected attempts until the first actual rejection after reaching D=N."""

    _check_positive_integer(N, "N")
    if not 0.0 < p < 1.0:
        raise ValueError("p must satisfy 0 < p < 1.")
    return float(N / p + 1.0 / (1.0 - p))


def n_boundary_star(K: int, p: float, eps: float) -> int:
    """Smallest integer N with boundary probability not larger than eps."""

    if not isinstance(K, int) or K < 1:
        raise ValueError("K must be a positive integer.")
    _check_probability(p, "p")
    if not 0.0 < eps < 1.0:
        raise ValueError("eps must satisfy 0 < eps < 1.")
    return int(binom.ppf(1.0 - eps, K, p)) + 1


def robust_boundary_probability(K: int, N: int, p: float, B: int) -> float:
    """Boundary probability under B deliberate suppressions and natural loss p."""

    if not isinstance(K, int) or K < 1:
        raise ValueError("K must be a positive integer.")
    _check_positive_integer(N, "N")
    _check_probability(p, "p")
    if not isinstance(B, int) or B < 0 or B > K:
        raise ValueError("B must satisfy 0 <= B <= K.")

    if B >= N:
        return 1.0
    return float(binom.sf(N - B - 1, K - B, p))


def robust_n_star(K: int, p: float, eps: float, B: int) -> int:
    """Smallest N that satisfies the boundary requirement under B suppressions."""

    if not isinstance(K, int) or K < 1:
        raise ValueError("K must be a positive integer.")
    _check_probability(p, "p")
    if not 0.0 < eps < 1.0:
        raise ValueError("eps must satisfy 0 < eps < 1.")
    if not isinstance(B, int) or B < 0 or B > K:
        raise ValueError("B must satisfy 0 <= B <= K.")

    return B + int(binom.ppf(1.0 - eps, K - B, p)) + 1


def ge_metrics(
    N: int,
    a: float,
    b: float,
    eG: float,
    eB: float,
    K: int = 1000,
) -> tuple[float, float, float]:
    """Return average loss, finite-horizon rejection, and mean rejection time.

    The channel uses two states, G and B. Message processing is evaluated in the
    current channel state and the channel then moves according to matrix A.
    """

    _check_positive_integer(N, "N")
    if not isinstance(K, int) or K < 1:
        raise ValueError("K must be a positive integer.")
    for value, name in ((a, "a"), (b, "b"), (eG, "eG"), (eB, "eB")):
        _check_probability(value, name)
    if a + b == 0:
        raise ValueError("a+b must be greater than zero.")

    A = np.array([[1.0 - a, a], [b, 1.0 - b]], dtype=float)
    E = np.diag([eG, eB])
    B0 = (np.eye(2) - E) @ A
    B1 = E @ A

    size = 2 * (N + 1)
    Q = np.zeros((size, size), dtype=float)
    for d in range(N):
        current = slice(2 * d, 2 * d + 2)
        same = slice(2 * d, 2 * d + 2)
        next_state = slice(2 * (d + 1), 2 * (d + 1) + 2)
        Q[current, same] = B0
        Q[current, next_state] = B1

    boundary = slice(2 * N, 2 * N + 2)
    Q[boundary, boundary] = B1

    pi = np.array([b / (a + b), a / (a + b)], dtype=float)
    alpha = np.zeros(size, dtype=float)
    alpha[:2] = pi
    ones = np.ones(size, dtype=float)

    p_bar = float(pi @ E @ np.ones(2))
    p_rejection = float(1.0 - alpha @ np.linalg.matrix_power(Q, K) @ ones)
    mean_attempts = float(alpha @ np.linalg.solve(np.eye(size) - Q, ones))
    return p_bar, p_rejection, mean_attempts



def monte_carlo_rejection(K: int, N: int, p: float, samples: int = 500_000, seed: int = 20260904) -> float:
    """Estimate the rejection probability using independent Monte Carlo trajectories.

    The boundary time follows a negative-binomial construction. After the N-th
    unprocessed message, the model waits for the first processed message, which
    causes the actual rejection.
    """

    if not isinstance(samples, int) or samples < 1:
        raise ValueError("samples must be a positive integer.")
    if not isinstance(seed, int):
        raise ValueError("seed must be an integer.")
    if not isinstance(K, int) or K < 0:
        raise ValueError("K must be a non-negative integer.")
    _check_positive_integer(N, "N")
    if not 0.0 < p < 1.0:
        raise ValueError("p must satisfy 0 < p < 1.")

    rng = np.random.default_rng(seed)
    processed_before_n_losses = rng.negative_binomial(N, p, size=samples)
    boundary_time = N + processed_before_n_losses
    wait_for_processed_message = rng.geometric(1.0 - p, size=samples)
    rejection_time = boundary_time + wait_for_processed_message
    return float(np.mean(rejection_time <= K))


def exhaustive_state_check(max_N: int = 8, max_K: int = 12) -> dict:
    """Check the cumulative synchronization invariant for all bounded traces.

    This function is intentionally exhaustive for small bounds. It is used as a
    computational check of the state update rule, not as a replacement for the
    mathematical proof in the paper.
    """

    import itertools

    _check_positive_integer(max_N, "max_N")
    _check_positive_integer(max_K, "max_K")

    checked = 0
    mismatches = 0

    for N in range(1, max_N + 1):
        for K in range(1, max_K + 1):
            for trace in itertools.product((0, 1), repeat=K):
                D = 0
                cumulative_losses = 0
                rejected = False

                for x in trace:
                    if rejected:
                        break
                    if D == N and x == 0:
                        rejected = True
                        break
                    if x == 1:
                        cumulative_losses += 1
                        D = min(N, D + 1)

                    if D != min(cumulative_losses, N):
                        mismatches += 1
                        break

                checked += 1

    return {
        "checked_traces": checked,
        "mismatches": mismatches,
        "max_N": max_N,
        "max_K": max_K,
    }

def m_tradeoff(M: int, login_bits: int = 2592, subsequent_bits: int = 1344) -> dict:
    """Return communication saving and linkability measures for parameter M."""

    _check_positive_integer(M, "M")
    if login_bits <= subsequent_bits or subsequent_bits <= 0:
        raise ValueError("Communication costs must satisfy login_bits > subsequent_bits > 0.")

    average_bits = (login_bits + M * subsequent_bits) / (M + 1)
    saving_fraction = M / (M + 1)
    linkability_lower_bound = (M - 1) / (M + 1)

    return {
        "M": M,
        "average_bits": float(average_bits),
        "saving_fraction": float(saving_fraction),
        "linkability_lower_bound": float(linkability_lower_bound),
    }
