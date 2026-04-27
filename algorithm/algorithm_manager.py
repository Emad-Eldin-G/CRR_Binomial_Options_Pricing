import streamlit as st
import numpy as np

from data.risk_free_rate import get_risk_free_rate
from data.stock_option_chain_data import get_stock_price
from algorithm.pricing import numba_price, get_put_price_from_call
from algorithm.volatility import crr_up_down, IVSurface
from algorithm.greeks import get_option_greeks


@st.cache_data(ttl="1d", show_spinner=False)
def iv_manager(ticker):
    """
    Implied Volatility Manager computes the implied volatility surface for the given ticker,
    and caches the result daily to avoid redundant computations during the day.

    Returns the grid data for plotting and the RBF interpolator for fast IV queries.
    """
    iv_surface = IVSurface(ticker)
    (XX, TT, IVgrid), rbf = iv_surface.main_iv_runner()
    return (XX, TT, IVgrid), rbf


def algorithm_manager(ticker, S0, K, T, optclass, N=1000):
    """
    Algorithm Manager orchestrates the entire option pricing process,
    It fetches the market risk free rate,
    computes the implied volatility surface and interpolator,
    and then uses the selected pricing algorithm to compute the option price and Greeks.
    """

    """
    Risk Free Rate
    """
    days_to_expiry = int(T * 365.25)
    r = get_risk_free_rate(days_to_expiry)
    st.session_state["risk_free_rate"] = float(np.round(r, 4))

    """
    Implied Volatility
    """
    st.session_state["iv_compute_on"] = True
    (XX, TT, IVgrid), rbf = iv_manager(ticker)
    S0 = get_stock_price(ticker)
    F = S0 * np.exp(r * T)  # Forward price
    moneyness = np.log(K / F)
    vol = (
        float(rbf(np.array([[moneyness, T]]))[0]) if rbf else 0.2
    )  # Fallback to 20% if RBF fails
    vol = np.float64(vol)  # Ensure it's a scalar float
    st.session_state["iv_compute_on"] = False


    dt = T / N
    u, d = crr_up_down(vol, dt)
    pricer = numba_price

    if pricer:
        if optclass == "E":
            # Can use parity to price other side (saves computation time for European options)
            call = pricer(S0, K, T, r, N, u, d, opttype="C", optclass=optclass)
            put = get_put_price_from_call(call, S0, K, r, T)
        elif optclass == "A":
            # Price call directly for American options
            put = pricer(S0, K, T, r, N, u, d, opttype="P", optclass=optclass)
            call = pricer(S0, K, T, r, N, u, d, opttype="C", optclass=optclass)
        else:
            st.warning("Invalid exercise type selected (must be 'E' or 'A').")
            return None, None

        greeks = get_option_greeks(
            S0, K, T, r, N, u, d, optclass=optclass, vol=vol, V0p=put, V0c=call
        )
        st.session_state["greeks"] = greeks

    else:
        call = None
        put = None

    st.session_state["option_price"] = [call, put]
    st.session_state["iv_value"] = vol
    st.session_state["iv_data"] = (XX, TT, IVgrid)
    st.session_state["S0"] = S0
    st.session_state["K"] = K
    st.session_state["T"] = T
    st.session_state["r"] = r
    st.session_state["vol"] = float(vol)
    st.session_state["optclass"] = optclass
    return call, put
