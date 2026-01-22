import streamlit as st

def option_inputs():
    st.title("Option Input Parameters")

    exercise = st.selectbox("Exercise Type", ["European", "American"])
    option_type = st.selectbox("Option Type", ["Call", "Put"])
    K = st.number_input("Strike Price (K)", min_value=1.0, value=100.0, help="The price at which the option can be exercised | K > 0")
    T = st.number_input("Time to Maturity (T)", min_value=0.03, max_value=50.00, value=1.00, step=0.01, help="Time in years until option expiration | T > 0")
    N = st.number_input("Number of Steps (N)", min_value=1, max_value=5000, value=50, help="Higher values increase accuracy but also computation time.")

    exercise_code = "E" if exercise == "European" else "A"
    option_code = "C" if option_type == "Call" else "P"

    return exercise_code, option_code, K, T, N
