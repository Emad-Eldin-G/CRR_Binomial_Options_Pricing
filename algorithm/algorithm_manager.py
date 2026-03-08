import streamlit as st
import numpy as np

from data.stock_option_chain_data import get_stock_price
from algorithm.pricing import np_price, get_put_price_from_call
from algorithm.volatility import crr_up_down, IVSurface
from algorithm.greeks import get_option_greeks, get_chain_greeks


@st.cache_data(ttl="1d", show_spinner=False)  # Data Cached on _date_key daily
def iv_manager(ticker):
    iv_surface = IVSurface(ticker)
    (XX, TT, IVgrid), rbf = iv_surface.main_iv_runner()
    return (XX, TT, IVgrid), rbf


def alogorithm_manager(ticker, S0, K, T, r, N, optclass):
    st.session_state["iv_compute_on"] = True
    (XX, TT, IVgrid), rbf = iv_manager(ticker)
    S0 = get_stock_price(ticker)

    F = S0 * np.exp(r * T)  # Forward price
    moneyness = np.log(K / F)

    vol = rbf(moneyness, T) if rbf else 0.2  # Fallback to 20% if RBF fails
    vol = np.float64(vol)  # Ensure it's a scalar float
    st.session_state["iv_compute_on"] = False

    dt = T / N
    u, d = crr_up_down(vol, dt)
    pricer = np_price

    if pricer:
        if optclass == "E":
            # Can use parity to price other side (saves computation time for European options)
            call = pricer(S0, K, T, r, N, u, d, opttype="C", optclass=optclass)
            put = get_put_price_from_call(call, S0, K, r, T)
            st.session_state["pc_parity"] = True
        elif optclass == "A":
            # Price call directly for American options
            put = pricer(S0, K, T, r, N, u, d, opttype="P", optclass=optclass)
            call = pricer(S0, K, T, r, N, u, d, opttype="C", optclass=optclass)
            st.session_state["pc_parity"] = False
        else:
            return st.warning("Invalid option type selected (must be 'C' or 'P').")

        greeks = get_option_greeks(
            S0, K, T, r, N, u, d, optclass=optclass, vol=vol, V0p=put, V0c=call
        )
        st.session_state["greeks"] = greeks

        chain_greeks = get_chain_greeks()
    else:
        call = None
        put = None

    st.session_state["option_price"] = [call, put]
    st.session_state["iv_value"] = vol
    st.session_state["iv_data"] = (XX, TT, IVgrid)
    st.session_state["rbf"] = rbf
    return call, put
