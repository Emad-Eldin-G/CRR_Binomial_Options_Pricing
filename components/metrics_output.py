import streamlit as st

@st.fragment
def compute_output(price_data):
    st.markdown(
        """
        <h2 style="text-align: center"><strong>Metrics</strong> </h2>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # computation running
    # -------------------------
    if st.session_state.get("price_compute_on"):

        # computation hasn’t finished yet
        if st.session_state.get("option_price") is None:
            with st.spinner("Computing option price..."):
                st.write("Calculating computation time...")
            return

        # computation has finished → show result
        result = st.session_state.option_price
        st.markdown(
            f"""
            <div style="padding: 5px; text-align: center; align-items: center;">
                <h2 style="color: #2196F3; font-size: 25px"><strong><section style="color: white; font-size: 25px">Runtime:</section> {st.session_state["runtime"]:.2f} secs</strong></h2>
                <h2 style="color: #2196F3; font-size: 25px"><strong><section style="color: white; font-size: 25px">Risk-Neutral Probability:</section> {result['rnp']:.3f}%</strong></h2>
            </div>
            """,
            unsafe_allow_html=True
        )
        return

    # -------------------------
    # idle state
    # -------------------------
    st.info("Time taken for computation will be displayed here.")
