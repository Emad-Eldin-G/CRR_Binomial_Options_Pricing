from scipy.stats import norm
from numba import njit, prange
import numpy as np


def black_scholes_price(S0, K, T, r, vol, opttype="C"):
    """
    Calculate the Black-Scholes price for European call or put options.

    BS is not used in the project, but it's included here for evaluation and comparison.
    """
    
    sqrtT = np.sqrt(T)
    vsqrtT = vol * sqrtT
    d1 = (np.log(S0 / K) + (r + 0.5 * vol * vol) * T) / vsqrtT
    d2 = d1 - vsqrtT
    disc = np.exp(-r * T)

    if opttype.upper().startswith("C"):
        return S0 * norm.cdf(d1) - K * disc * norm.cdf(d2)
    else:
        return K * disc * norm.cdf(-d2) - S0 * norm.cdf(-d1)


def dp_price(S0, K, T, r, N, u, d, opttype="C", optclass="E"):
    """
    Calculate the option price using a dynamic programming approach.
    (slowest)
    """

    dt = T / N
    q = (np.exp(r * dt) - d) / (u - d)  # risk-neutral probability
    discount = np.exp(-r * dt)

    # Initialize asset prices at maturity
    S = np.zeros(N + 1)  # [0, 0, .. N]
    S[0] = S0 * (d**N)  # [S0, 0, .. N]

    # Build the asset price tree
    for down_move in range(1, N + 1):
        # Going up the tree
        S[down_move] = S[down_move - 1] * (u / d)

    # Initialize option values at maturity
    option_values = np.zeros(N + 1)  # [0, 0, .. N]
    for up_move in range(N + 1):
        if opttype == "C":
            option_values[up_move] = max(0, S[up_move] - K)
        else:
            option_values[up_move] = max(0, K - S[up_move])

    # Backward induction
    for step in range(N - 1, -1, -1):
        for up_move in range(step + 1):
            option_values[up_move] = discount * (
                q * option_values[up_move + 1] + (1 - q) * option_values[up_move]
            )  # binomial formula

            if optclass == "A":
                # American option early exercise check
                if opttype == "C":
                    option_values[up_move] = max(
                        option_values[up_move],
                        S0 * (u**up_move) * (d ** (step - up_move)) - K,
                    )
                else:
                    option_values[up_move] = max(
                        option_values[up_move],
                        K - S0 * (u**up_move) * (d ** (step - up_move)),
                    )
            else:
                pass  # European option, no early exercise

    return np.float64(option_values[0])


def np_price(S0, K, T, r, N, u, d, opttype="C", optclass="E"):
    """
    Calculate the option price using a vectorized approach with NumPy
    (fast than dp_price)
    """

    dt = T / N
    q = (np.exp(r * dt) - d) / (u - d)
    discount = np.exp(-r * dt)

    # Initialize asset prices at maturity (use log-space to avoid overflow)
    j = np.arange(N + 1)
    log_S = np.log(S0) + j * np.log(u) + (N - j) * np.log(d)
    S = np.exp(log_S)

    # Initialize option values at maturity
    if opttype == "C":
        option_values = np.maximum(0.0, S - K)
    else:
        option_values = np.maximum(0.0, K - S)

    # Backward induction
    for step in range(N - 1, -1, -1):
        option_values[: step + 1] = discount * (
            q * option_values[1 : step + 2] + (1 - q) * option_values[: step + 1]
        )

        # American early exercise check (also vectorized)
        if optclass == "A":
            j = np.arange(step + 1)
            S_ij = S0 * (u**j) * (d ** (step - j))  # stock price at node (i, j)

            if opttype == "C":
                exercise = np.maximum(S_ij - K, 0.0)
            else:
                exercise = np.maximum(K - S_ij, 0.0)

            option_values[: step + 1] = np.maximum(option_values[: step + 1], exercise)

    return np.float64(option_values[0])


@njit(cache=True)
def numba_price(S0, K, T, r, N, u, d, opttype="C", optclass="E"):
    """
    Calculate the option price using a vectorized approach with NumPy,
    alongside JIT Numba compilation for maximum performance.
    (fastest)
    """

    dt = T / N
    q = (np.exp(r * dt) - d) / (u - d)
    discount = np.exp(-r * dt)

    # Initialize asset prices at maturity (use log-space to avoid overflow)
    j = np.arange(N + 1)
    log_S = np.log(S0) + j * np.log(u) + (N - j) * np.log(d)
    S = np.exp(log_S)

    # Initialize option values at maturity
    if opttype == "C":
        option_values = np.maximum(0.0, S - K)
    else:
        option_values = np.maximum(0.0, K - S)

    # Backward induction
    for step in range(N - 1, -1, -1):
        option_values[: step + 1] = discount * (
            q * option_values[1 : step + 2] + (1 - q) * option_values[: step + 1]
        )

        # American early exercise check (also vectorized)
        if optclass == "A":
            j = np.arange(step + 1)
            S_ij = S0 * (u**j) * (d ** (step - j))  # stock price at node (i, j)

            if opttype == "C":
                exercise = np.maximum(S_ij - K, 0.0)
            else:
                exercise = np.maximum(K - S_ij, 0.0)

            option_values[: step + 1] = np.maximum(option_values[: step + 1], exercise)

    return np.float64(option_values[0])


@njit(cache=True)
def numba_price_core(S0, K, T, r, N, u, d, opttype, optclass):
    """
    Low-level Numba kernel for binomial pricing.
    Designed to be called inside prange (parallel-safe, no Python features).
    """
    dt = T / N
    q = (np.exp(r * dt) - d) / (u - d)
    discount = np.exp(-r * dt)

    j = np.arange(N + 1)
    log_S = np.log(S0) + j * np.log(u) + (N - j) * np.log(d)
    S = np.exp(log_S)

    if opttype == "C":
        option_values = np.maximum(0.0, S - K)
    else:
        option_values = np.maximum(0.0, K - S)

    for step in range(N - 1, -1, -1):
        option_values[:step + 1] = discount * (
            q * option_values[1:step + 2] + (1 - q) * option_values[:step + 1]
        )
        if optclass == "A":
            j = np.arange(step + 1)
            S_ij = S0 * (u ** j) * (d ** (step - j))
            if opttype == "C":
                exercise = np.maximum(S_ij - K, 0.0)
            else:
                exercise = np.maximum(K - S_ij, 0.0)
            option_values[:step + 1] = np.maximum(option_values[:step + 1], exercise)

    return np.float64(option_values[0])


@njit(parallel=True, cache=True)
def numba_price_batch(S_arr, K, T_arr, r, N, u_arr, d_arr, opttype, optclass):
    """
    Price an array of (S, T, u, d) combinations in parallel.
    prange distributes cells across CPU cores via numba's thread pool — no GIL.
    """
    n = len(S_arr)
    out = np.empty(n)
    for k in prange(n):
        out[k] = numba_price_core(S_arr[k], K, T_arr[k], r, N, u_arr[k], d_arr[k], opttype, optclass)
    return out


def put_call_parity(S0, K, T, r, call_price, put_price, optclass="E") -> None | float:
    """
    Calculate the put-call parity.

    LHS = C + Ke^(-rT)
    RHS = P + S0
    """

    if optclass != "E":
        return None

    lhs = call_price + (K * np.exp(-r * T))
    rhs = put_price + S0
    return np.isclose(lhs, rhs)


def get_put_price_from_call(call_price, S0, K, r, T):
    """Calculate put price from call price using put-call parity."""
    return np.float64(call_price + K * np.exp(-r * T) - S0)
