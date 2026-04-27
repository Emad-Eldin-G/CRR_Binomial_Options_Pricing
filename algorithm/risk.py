import numpy as np
from algorithm.pricing import numba_price, numba_price_batch
from algorithm.volatility import crr_up_down

N_STEPS = 2000

def pnl_summary(S0, K, T, r, vol, call_price, put_price, greeks_dict):
    """
    Trader-facing metrics for a single option position (100 shares).

    Calculates:
    - Time to expiry (days)
    - Moneyness (% OTM)
    - Breakeven price and % move to breakeven
    - Hedge ratio (shares per contract)
    - Intrinsic vs time value split
    - Dollar Vega and Theta per contract (if not near expiry)
    """

    days_to_expiry = max(int(round(T * 365.25)), 0)
    near_expiry = days_to_expiry <= 1

    # Positive = OTM, negative = ITM
    call_otm_pct = (K / S0 - 1) * 100
    put_otm_pct  = (S0 / K - 1) * 100

    breakeven_call   = K + call_price
    breakeven_put    = K - put_price
    
    be_call_move_pct = (breakeven_call - S0) / S0 * 100
    be_put_move_pct  = (breakeven_put  - S0) / S0 * 100

    call_already_itm = S0 > K
    put_already_itm  = S0 < K

    def gv(name, side):
        """
        Helper to safely extract a Greek value from the greeks_dict, 
        returning 0.0 if any key is missing or if the value is not a valid number.
        """
        v = greeks_dict.get(name, {}) if isinstance(greeks_dict, dict) else {}
        try:
            return float(v.get(side, 0.0))
        except Exception:
            return 0.0

    delta_c = gv("delta", "c");  delta_p = gv("delta", "p")
    theta_c = gv("theta", "c");  theta_p = gv("theta", "p")
    vega_c  = gv("vega",  "c");  vega_p  = gv("vega",  "p")

    # floor(|Δ| × 100) shares per contract
    hedge_call = np.floor(abs(delta_c) * 100)
    hedge_put  = np.floor(abs(delta_p) * 100)

    intrinsic_call = max(S0 - K, 0.0)
    intrinsic_put  = max(K - S0, 0.0)

    # Clamp to zero — negative time value is a binomial rounding artefact at low T
    time_val_call  = max(call_price - intrinsic_call, 0.0)
    time_val_put   = max(put_price  - intrinsic_put,  0.0)

    if near_expiry:
        dollar_vega_call = dollar_vega_put = 0.0
        theta_day_call   = theta_day_put   = None
    else:
        dollar_vega_call = vega_c * 100   # $/1pp vol move per contract
        dollar_vega_put  = vega_p * 100
        theta_day_call   = theta_c * 100  # $/day per contract
        theta_day_put    = theta_p * 100


    return dict(
        days_to_expiry=days_to_expiry,
        near_expiry=near_expiry,
        
        call_otm_pct=call_otm_pct,
        put_otm_pct=put_otm_pct,

        call_already_itm=call_already_itm,
        put_already_itm=put_already_itm,

        breakeven_call=breakeven_call,
        breakeven_put=breakeven_put,

        be_call_move_pct=be_call_move_pct,
        be_put_move_pct=be_put_move_pct,

        hedge_call=hedge_call,
        hedge_put=hedge_put,

        intrinsic_call=intrinsic_call,
        intrinsic_put=intrinsic_put,

        time_val_call=time_val_call,
        time_val_put=time_val_put,

        dollar_vega_call=dollar_vega_call,
        dollar_vega_put=dollar_vega_put,

        theta_day_call=theta_day_call,
        theta_day_put=theta_day_put,

        max_loss_call=call_price * 100,
        max_loss_put=put_price  * 100,

        call_price=call_price,
        put_price=put_price,
    )


def pnl_scenario_matrix(S0, K, T, r, vol, call_price, put_price, optclass="E"):
    """
    P&L heatmap over a grid of spot shocks (%) × vol shocks (pp).
    Reference prices use N_STEPS so the central cell is exactly 0.
    Returns call_pnl, put_pnl, spot_shocks, vol_shocks.
    """
    spot_shocks = np.linspace(-0.20, 0.20, 9)
    vol_shocks  = np.linspace(-0.10, 0.10, 7)

    u_ref, d_ref = crr_up_down(vol, T / N_STEPS)
    call_ref = numba_price(S0, K, T, r, N_STEPS, u_ref, d_ref, "C", optclass)
    put_ref  = numba_price(S0, K, T, r, N_STEPS, u_ref, d_ref, "P", optclass)

    # Pre-compute (u, d) per vol shock
    ud = {dv: crr_up_down(max(vol + dv, 0.01), T / N_STEPS) for dv in vol_shocks}

    # Build flat arrays of shape (n_vol_shocks × n_spot_shocks,)
    S_arr = np.array([S0 * (1 + ds) for dv in vol_shocks for ds in spot_shocks])
    u_arr = np.array([ud[dv][0]     for dv in vol_shocks for ds in spot_shocks])
    d_arr = np.array([ud[dv][1]     for dv in vol_shocks for ds in spot_shocks])

    T_arr = np.full(len(S_arr), T)
    call_vals = numba_price_batch(S_arr, K, T_arr, r, N_STEPS, u_arr, d_arr, "C", optclass)
    put_vals  = numba_price_batch(S_arr, K, T_arr, r, N_STEPS, u_arr, d_arr, "P", optclass)

    call_pnl = call_vals.reshape(len(vol_shocks), len(spot_shocks)) - call_ref
    put_pnl  = put_vals.reshape(len(vol_shocks), len(spot_shocks))  - put_ref

    return call_pnl, put_pnl, spot_shocks, vol_shocks
