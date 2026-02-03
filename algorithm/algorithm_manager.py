import streamlit as st
from .pricing import dp_price, np_price, cpp_price, black_scholes_price
from .volatility import crr_up_down
from algorithm.arbitrage import put_call_parity


PRICERS = {
    "Python DP": dp_price,
    "NumPy Vectorization": np_price,
    "C++": cpp_price,
}


def alogorithm_manager(S0, K, T, r, N, optclass, method=None):
    method = method or st.session_state.get("method", "Python DP")
    if isinstance(method, tuple):
        method = method[0]
    
    vol = st.session_state.get("volatility", 0.2)  # Default volatility if not set

    dt = T / N
    u, d = crr_up_down(vol, dt)
    pricer = PRICERS.get(method)

    if pricer:
        call = pricer(S0, K, T, r, N, u, d, opttype="C", optclass=optclass)
        put = pricer(S0, K, T, r, N, u, d, opttype="P", optclass=optclass)
    else:
        call = None
        put = None

    pc_parity = put_call_parity(S0, K, T, r, call, put, optclass)

    st.session_state["arb_metrics"] = {"pc_parity": pc_parity}
    st.session_state["option_price"] = [call, put]
    return call, put
