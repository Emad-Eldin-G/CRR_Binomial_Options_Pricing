import streamlit as st

from components.stock_inputs import stock_inputs
from components.option_inputs import option_inputs
from components.market_inputs import market_inputs
from components.algorithm_inputs import algorithm_inputs

from components.price_output import price_output
from components.metrics_output import compute_output
from components.binomial_tree_output import binomial_tree_output

from algorithm.algorithm_manager import alogorithm_manager

st.session_state.setdefault("option_price", None)
st.session_state.setdefault("price_compute_on", False)

st.set_page_config(
    page_title="Binomial Option Pricing",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Cox, Ross and Rubinstein Binomial Method for Options Pricing 💲📈")

st.sidebar.image("./static/uni_logo.jpg")
st.sidebar.markdown("""
## Computer Science Final Year Project  
### Emadeldin Osman (eo161)
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
            alogorithm_manager(S0, K, T, r, N, vol, option_type, exercise)


with st.container(border=True, horizontal=True):
    price_output(st.session_state.get("option_price", {}))
    compute_output(st.session_state.get("option_price", {}))

with st.container(border=True):
    binomial_tree_output(st.session_state.get("binomial_tree", None))
