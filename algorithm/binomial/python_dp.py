from mock.option_price import mock_price
import streamlit as st

def dp_price():
    if st.session_state["Prod"]:
        # Placeholder for actual DP binomial pricing logic
        pass
    else:
        p = mock_price()
        return mock_price()