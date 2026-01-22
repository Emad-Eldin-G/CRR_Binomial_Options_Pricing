import streamlit as st
import time

@st.fragment
def price_output(price_data):
    st.markdown(
        """
        <h2 style="text-align: center"><strong>Option Price</strong> </h2>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # computation running
    # -------------------------
    if st.session_state.get("price_compute_on"):

        # Price has not yet been computed
        if st.session_state.get("option_price") is None:
            with st.spinner("Waiting for option price computation..."):
                st.write("Calculating...")
            return
        
        # Price is now ready
        result = st.session_state.option_price
        st.markdown(
            f"""
            <div style="padding: 10px; text-align: center;">
                <h2 style="color: #4CAF50; font-size: 80px"><strong>${result["price"]:.4f}</strong></h2>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # -------------------------
    # idle state
    # -------------------------
    st.info("Option price will be displayed here after computation.")
