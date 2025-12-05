import streamlit as st

def market_inputs():
    st.title("Market Input Parameters")
    r = st.number_input("Risk-Free Rate (r)", min_value=0.001, max_value=0.30, value=0.001, step=0.01)
    return r
