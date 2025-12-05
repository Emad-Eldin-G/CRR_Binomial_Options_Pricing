import streamlit as st
import time

from components.stock_inputs import stock_inputs
from components.option_inputs import option_inputs
from components.market_inputs import market_inputs
from components.algorithm_inputs import algorithm_inputs

st.set_page_config(
    page_title="Binomial Option Pricing",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Cox, Ross and Rubinstein Binomial Method for Options Pricing 💲📈")

st.sidebar.markdown("""
### Created by [Emadeldin Osman](https://github.com/Emad-Eldin-G)
""")

with st.sidebar.container():
    
    S0, vol = stock_inputs()
    exercise, option_type, K, T, N = option_inputs()
    r = market_inputs()
    method = algorithm_inputs()

    with st.container(vertical_alignment="center", horizontal_alignment="center"):
        st.container(height=5, border=False) # Spacer for visual purposes
        st.button("Compute Option Price", type="primary", width="stretch")


with st.container(border=True, horizontal=True):
    with st.container():
        st.header("Option Price Output")
        if st.session_state.get("price_compute_on"):
            while st.session_state.get("price_compute_on"):
                with st.spinner("Computing option price..."):
                    # Placeholder for actual computation logic
                    time.sleep(2)  # Simulate computation delay
                    st.session_state.option_price = 42.00  # Dummy option price
                    st.session_state.price_compute_on = False  # Turn off the loop
            
            st.success(f"The computed option price is: ${st.session_state.option_price}", )
        else:
            st.info("Option price will be displayed here after computation.")

    with st.container():
        st.header("Computation Time")
        st.info("Time taken for computation will be displayed here.")

tree_continaer = st.container(border=True)
with tree_continaer:
    st.header("Binomial Tree Visualization", help="Visual representation of the binomial tree used in option pricing, with the up and down values at each node.")
    st.info("Binomial tree visualization will be displayed here.")
