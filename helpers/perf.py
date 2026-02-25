from time import time
from functools import wraps
import streamlit as st


def calc_runtime(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        end_time = time()
        st.session_state["runtime"] = end_time - start_time
        return result

    return wrapper
