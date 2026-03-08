import numpy as np
import pandas as pd
import numba as nb
from algorithm.volatility import crr_up_down
from algorithm.pricing import np_price


def get_option_greeks(
    S0,
    K,
    T,
    r,
    N,
    u,
    d,
    vol,  # pass your IV here; if None we'll infer from u
    V0p,
    V0c,
    optclass="E",
    bumpV_rel=1e-2,  # 1% spot bump for delta
    bumpG_rel=5e-3,  # 0.5% spot bump for gamma
    bumpSig=1e-2,  # 1 vol point (0.01) for vega
    bumpT=1 / 365,  # 1 day (in years) for theta
) -> dict[str, dict[str, float]]:

    # ---- Delta ----
    bumpV = bumpV_rel * S0
    Vp_c = np_price(S0 + bumpV, K, T, r, N, u, d, "C", optclass)
    Vm_c = np_price(S0 - bumpV, K, T, r, N, u, d, "C", optclass)
    Vp_p = np_price(S0 + bumpV, K, T, r, N, u, d, "P", optclass)
    Vm_p = np_price(S0 - bumpV, K, T, r, N, u, d, "P", optclass)

    delta_c = (Vp_c - Vm_c) / (2.0 * bumpV)
    delta_p = (Vp_p - Vm_p) / (2.0 * bumpV)

    # ---- Gamma ----
    bumpG = bumpG_rel * S0
    Vp_cg = np_price(S0 + bumpG, K, T, r, N, u, d, "C", optclass)
    Vm_cg = np_price(S0 - bumpG, K, T, r, N, u, d, "C", optclass)
    Vp_pg = np_price(S0 + bumpG, K, T, r, N, u, d, "P", optclass)
    Vm_pg = np_price(S0 - bumpG, K, T, r, N, u, d, "P", optclass)

    gamma_c = (Vp_cg - 2.0 * V0c + Vm_cg) / (bumpG * bumpG)
    gamma_p = (Vp_pg - 2.0 * V0p + Vm_pg) / (bumpG * bumpG)

    # ---- Vega ----
    vol_p = vol + bumpSig
    vol_m = max(1e-12, vol - bumpSig)
    dt = T / N

    u_p, d_p = crr_up_down(vol_p, dt)
    u_m, d_m = crr_up_down(vol_m, dt)

    Vsig_p_c = np_price(S0, K, T, r, N, u_p, d_p, "C", optclass)
    Vsig_m_c = np_price(S0, K, T, r, N, u_m, d_m, "C", optclass)
    Vsig_p_p = np_price(S0, K, T, r, N, u_p, d_p, "P", optclass)
    Vsig_m_p = np_price(S0, K, T, r, N, u_m, d_m, "P", optclass)

    vega_c = (Vsig_p_c - Vsig_m_c) / (2.0 * bumpSig) * 0.01
    vega_p = (Vsig_p_p - Vsig_m_p) / (2.0 * bumpSig) * 0.01

    # ---- Theta ----
    bumpT = min(bumpT, 0.49 * T) if T > 0 else bumpT
    Tp = T + bumpT
    Tm = max(1e-12, T - bumpT)

    dtp, dtm = Tp / N, Tm / N
    up, dp = crr_up_down(vol, dtp)
    um, dm = crr_up_down(vol, dtm)

    VTp_c = np_price(S0, K, Tp, r, N, up, dp, "C", optclass)
    VTm_c = np_price(S0, K, Tm, r, N, um, dm, "C", optclass)
    VTp_p = np_price(S0, K, Tp, r, N, up, dp, "P", optclass)
    VTm_p = np_price(S0, K, Tm, r, N, um, dm, "P", optclass)

    # Theta = -dV/dT (per year)
    theta_c = -(VTp_c - VTm_c) / (2.0 * bumpT)
    theta_p = -(VTp_p - VTm_p) / (2.0 * bumpT)

    return {
        "delta": {"c": float(delta_c), "p": float(delta_p)},
        "gamma": {"c": float(gamma_c), "p": float(gamma_p)},
        "vega": {"c": float(vega_c), "p": float(vega_p)},
        "theta": {"c": float(theta_c), "p": float(theta_p)},
    }


def get_chain_greeks():
    pass
