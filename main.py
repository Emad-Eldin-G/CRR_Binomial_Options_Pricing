import streamlit as st

from components.input_components import (
    stock_inputs,
    option_inputs,
    market_inputs,
    algorithm_inputs,
)
from components.output_components import (
    price_output,
    runtime_output,
    greeks_output,
    binomial_tree_output,
)

from algorithm.algorithm_manager import alogorithm_manager

st.session_state.setdefault("option_price", None)
st.session_state.setdefault("price_compute_on", False)

st.set_page_config(
    page_title="Binomial Option Pricing",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Cox, Ross and Rubinstein Binomial Method for Options Pricing 💲📈")

st.sidebar.markdown("""
### Emadeldin Osman
""")

with st.sidebar.container():
    
    S0, vol = stock_inputs()
    exercise, option_type, K, T, N = option_inputs()
    r = market_inputs()
    method = algorithm_inputs()

    with st.container(vertical_alignment="center", horizontal_alignment="center"):
        st.container(height=5, border=False) # Spacer for visual purposes
        price_button = st.button("Compute Option Price", type="primary", width="stretch")
        if price_button:
            st.session_state.price_compute_on = True
            alogorithm_manager(S0, K, T, r, N, vol, option_type, exercise, method=method)


st.divider()
price_data = st.session_state.get("option_price")

c1, c2 = st.columns(2)
with c1:
    price_output(price_data)
with c2:
    runtime_output(price_data)

st.divider()
greeks_output(price_data)

st.divider()
binomial_tree_output(st.session_state.get("binomial_tree"))
