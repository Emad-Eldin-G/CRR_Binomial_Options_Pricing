import numpy as np
import pandas as pd
import numba as nb
from .pricing import np_price

def get_greeks(S0, K, T, r, N, u, d, optclass="E", vol=0.0, V0p=0.0, V0c=0.0):
    bumpV = 1e-2 * S0
    bumpG = 5e-3 * S0
    
    bumps = np.array([
        []
    ])

    Vp_c = np_price(S0 + bumpV, K, T, r, N, u, d, "C", optclass)
    Vm_c = np_price(S0 - bumpV, K, T, r, N, u, d, "C", optclass)
    
    Vp_p = np_price(S0 + bumpV, K, T, r, N, u, d, "P", optclass)
    Vm_p = np_price(S0 - bumpV, K, T, r, N, u, d, "P", optclass)


    delta_c = (Vp_c - Vm_c) / (2.0 * bumpV)
    gamma_c = (Vp_c - 2.0 * V0c + Vm_c) / (bumpG * bumpG)

    delta_p = (Vp_p - Vm_p) / (2.0 * bumpV)
    gamma_p = (Vp_p - 2.0 * V0p + Vm_p) / (bumpG * bumpG)

    return {
        "delta": {"c": delta_c, "p": delta_p},
        "gamma": {"c": gamma_c, "p": gamma_p}
    }