import streamlit as st

def algorithm_inputs():
    st.title("Algorithm Parameters")

    options = [
    ("Python DP", 1),
    ("NumPy Vectorization", 2),
    ("C++", 3)
]

    method = st.selectbox("Computation Method", options, format_func=lambda x: x[0])

    with st.expander("About Computation Methods"):
        st.markdown("""
        - **Python DP**: Basic dynamic programming approach  
        - **NumPy Vectorization**: Uses array operations for speed  
        - **C++**: High-performance compiled implementation  
        """)

    return method
