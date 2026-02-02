import streamlit as st
from algorithm import python_dp, python_numpy, cpp
from algorithm.volatility import crr_up_down


PRICERS = {
    "Python DP": python_dp.dp_price,
    "NumPy Vectorization": python_numpy.np_price,
    "Python NumPy": python_numpy.np_price,  # alias
    "C++": cpp.cpp_price,
}


def alogorithm_manager(S0, K, T, r, N, vol, opttype, optclass, method=None):
    method = method or st.session_state.get("method", "Python DP")
    if isinstance(method, tuple):
        method = method[0]

    dt = T / N
    u, d = crr_up_down(vol, dt)
    pricer = PRICERS.get(method)

    if pricer:
        price = pricer(S0, K, T, r, N, u, d, opttype, optclass)
    else:
        price = None

    st.session_state["option_price"] = price
    return price
