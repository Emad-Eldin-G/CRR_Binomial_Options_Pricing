import streamlit as st
import time
from .binomial import python_dp, cpp, python_numpy
from .black_scholes import bs

def alogorithm_manager():
    method = st.session_state.get("method", "Python DP")
    
    if method == "Python DP":
        price = python_dp.dp_price()
    elif method == "C++":
        price = cpp.cpp_price()
    elif method == "Python NumPy":
        price = python_numpy.numpy_price()
    elif method == "Black-Scholes":
        price = bs.bs_price()
    else:
        price = None
    
    st.session_state["option_price"] = price
    return price