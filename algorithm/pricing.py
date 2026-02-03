from functools import lru_cache
from helpers.perf import calc_runtime
from scipy.stats import norm
import numpy as np


@lru_cache(maxsize=32)
def black_scholes_price(S0, K, T, r, vol, opttype='C'):
    sqrtT = np.sqrt(T)
    vsqrtT = vol * sqrtT
    d1 = (np.log(S0 / K) + (r + 0.5 * vol * vol) * T) / vsqrtT
    d2 = d1 - vsqrtT
    disc = np.exp(-r * T)

    if opttype.upper().startswith("C"):
        return S0 * norm(d1) - K * disc * norm(d2)
    else:
        return K * disc * norm(-d2) - S0 * norm(-d1)

@lru_cache(maxsize=32)
@calc_runtime
def dp_price(S0, K, T, r, N, u, d, opttype='C', optclass="E"):
    dt = T / N
    q = (np.exp(r * dt) - d) / (u - d)  # risk-neutral probability
    discount = np.exp(-r * dt)

    # Initialize asset prices at maturity
    S = np.zeros(N + 1)  # [0, 0, .. N]
    S[0] = S0 * (d ** N)  # [S0, 0, .. N]

    # Build the asset price tree
    for up_move in range(1, N+1):
        # Going up the tree
        S[up_move] = S[up_move - 1] * (u / d)

    # Initialize option values at maturity
    option_values = np.zeros(N + 1)  # [0, 0, .. N]
    for up_move in range(N + 1):
        if opttype == 'C':
            option_values[up_move] = max(0, S[up_move] - K)
        else:
            option_values[up_move] = max(0, K - S[up_move])

    # Backward induction
    for step in range(N - 1, -1, -1):
        for up_move in range(step + 1):
            option_values[up_move] = discount * (q * option_values[up_move + 1] + (1 - q) * option_values[up_move])  # binomial formula

            if optclass == "A":
                # American option early exercise check
                if opttype == 'C':
                    option_values[up_move] = max(
                        option_values[up_move], 
                        S0 * (u ** up_move) * (d ** (step - up_move)) - K
                        )
                else:
                    option_values[up_move] = max(
                        option_values[up_move], 
                        K - S0 * (u ** up_move) * (d ** (step - up_move))
                        )
            else:
                pass  # European option, no early exercise

    return float(np.round(option_values[0], 4))

@lru_cache(maxsize=32)
@calc_runtime
def np_price(S0, K, T, r, N, u, d, opttype='C', optclass="E"):
    dt = T / N
    q = (np.exp(r * dt) - d) / (u - d)
    discount = np.exp(-r * dt)

    # Initialize asset prices at maturity
    j = np.arange(N + 1)
    S = S0 * (u ** j) * (d ** (N - j))

    # Initialize option values at maturity
    if opttype == 'C':
        option_values = np.maximum(0.0, S - K)
    else:
        option_values = np.maximum(0.0, K - S)

    # Backward induction
    for step in range(N - 1, -1, -1):
        option_values[:step+1] = discount * (
            q * option_values[1:step+2] + (1 - q) * option_values[:step+1]
        )

        # American early exercise check (also vectorized)
        if optclass == "A":
            j = np.arange(step + 1)
            S_ij = S0 * (u ** j) * (d ** (step - j))  # stock price at node (i, j)

            if opttype == "C":
                exercise = np.maximum(S_ij - K, 0.0)
            else:
                exercise = np.maximum(K - S_ij, 0.0)

            option_values[:step+1] = np.maximum(option_values[:step+1], exercise)

    return float(np.round(option_values[0], 4))

def cpp_price(S0, K, T, r, N, u, d, opttype="C", optclass="E"):
    # Will use C++ Python bindings when available
    return np_price(S0, K, T, r, N, u, d, opttype, optclass)