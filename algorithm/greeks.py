import numpy as np
from algorithm.volatility import crr_up_down
from algorithm.pricing import numba_price_batch


def get_option_greeks(
        S0, 
        K, 
        T, 
        r, 
        N, 
        u, 
        d, 
        vol, 
        V0p, 
        V0c, 
        optclass="E", 
        bumpV_rel=1e-2, 
        bumpG_rel=5e-3, 
        bumpSig=1e-2, 
        bumpT=1 / 365.25
    ) -> dict[str, dict[str, float]]:
    """
    Computing option Greeks (delta, gamma, vega, theta) using finite differences on the binomial tree.
    Using parallel batch pricing to compute all bumped prices in one go for efficiency.
    """

    # Near-expiry guard.
    NEAR_EXPIRY_THRESHOLD = 2 / 365.25  # 2 calendar days
    near_expiry = T <= NEAR_EXPIRY_THRESHOLD
    
    if near_expiry:
        # Only delta is reliable near expiry
        # Other Greek suppressed
        bumpV = bumpV_rel * S0
        S_arr = np.array([S0 + bumpV, S0 - bumpV])
        T_arr = np.array([T, T])
        u_arr = np.array([u, u])
        d_arr = np.array([d, d])

        c = numba_price_batch(S_arr, K, T_arr, r, N, u_arr, d_arr, "C", optclass)
        p = numba_price_batch(S_arr, K, T_arr, r, N, u_arr, d_arr, "P", optclass)

        return {
            "delta": {"c": float((c[0] - c[1]) / (2.0 * bumpV)),
                      "p": float((p[0] - p[1]) / (2.0 * bumpV))},
            "gamma": {"c": 0.0, "p": 0.0},
            "vega":  {"c": 0.0, "p": 0.0},
            "theta": {"c": 0.0, "p": 0.0},
        }

    # ---- Pre-compute bump parameters ----------------------------------------
    bumpV = bumpV_rel * S0
    bumpG = bumpG_rel * S0

    vol_p = vol + bumpSig
    vol_m = max(1e-12, vol - bumpSig)
    dt = T / N

    u_p, d_p = crr_up_down(vol_p, dt)
    u_m, d_m = crr_up_down(vol_m, dt)

    Tp = T + bumpT
    Tm = max(1e-12, T - bumpT)

    up, dp = crr_up_down(vol, Tp / N)
    um, dm = crr_up_down(vol, Tm / N)

    # ---- Pack all 8 bump evaluations per side into flat arrays ---------------
    S_arr = np.array([S0 + bumpV, S0 - bumpV,
                             S0 + bumpG, S0 - bumpG,
                             S0,         S0,
                             S0,         S0])
    
    T_arr = np.array([T,  T,  T,  T,  T,  T,  Tp, Tm])
    u_arr = np.array([u,  u,  u,  u,  u_p, u_m, up, um])
    d_arr = np.array([d,  d,  d,  d,  d_p, d_m, dp, dm])

    c = numba_price_batch(S_arr, K, T_arr, r, N, u_arr, d_arr, "C", optclass)
    p = numba_price_batch(S_arr, K, T_arr, r, N, u_arr, d_arr, "P", optclass)

    # ---- Finite differences --------------------------------------------------
    delta_c = (c[0] - c[1]) / (2.0 * bumpV)
    delta_p = (p[0] - p[1]) / (2.0 * bumpV)

    gamma_c = (c[2] - 2.0 * V0c + c[3]) / (bumpG * bumpG)
    gamma_p = (p[2] - 2.0 * V0p + p[3]) / (bumpG * bumpG)

    vega_c = (c[4] - c[5]) / (2.0 * bumpSig) * 0.01
    vega_p = (p[4] - p[5]) / (2.0 * bumpSig) * 0.01

    # Divide by 365.25 to convert from $/year/share → $/day/share.
    theta_c = -(c[6] - c[7]) / (2.0 * bumpT) / 365.25
    theta_p = -(p[6] - p[7]) / (2.0 * bumpT) / 365.25

    return {
        "delta": {"c": float(delta_c), "p": float(delta_p)},
        "gamma": {"c": float(gamma_c), "p": float(gamma_p)},
        "vega":  {"c": float(vega_c),  "p": float(vega_p)},
        "theta": {"c": float(theta_c), "p": float(theta_p)},
    }

