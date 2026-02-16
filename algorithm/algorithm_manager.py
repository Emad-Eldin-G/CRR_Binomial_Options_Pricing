import streamlit as st
from .pricing import np_price, get_call_price_from_put, get_put_price_from_call
from .volatility import crr_up_down
from algorithm.arbitrage import put_call_parity

def alogorithm_manager(S0, K, T, r, N, vol, optclass):
    dt = T / N
    u, d = crr_up_down(vol, dt)
    pricer = np_price

    if pricer:
        if optclass == "E":
            # Can use parity to price other side (saves computation time for European options)
            call = pricer(S0, K, T, r, N, u, d, opttype="C", optclass=optclass)
            put = get_put_price_from_call(call, S0, K, r, T)
        elif optclass == "A":
            # Price call directly for American options
            put = pricer(S0, K, T, r, N, u, d, opttype="P", optclass=optclass)
            call = pricer(S0, K, T, r, N, u, d, opttype='C', optclass=optclass)
        else:
            return st.warning("Invalid option type selected (must be 'C' or 'P').")
    else:
        call = None
        put = None

    pc_parity = put_call_parity(S0, K, T, r, call, put, optclass)

    st.session_state["arb_metrics"] = {"pc_parity": pc_parity}
    st.session_state["option_price"] = [call, put]
    return call, put
