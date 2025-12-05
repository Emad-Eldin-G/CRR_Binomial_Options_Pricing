import streamlit as st


@st.fragment
def binomial_tree_output(tree_data):
    st.markdown(
        """
        <h2 style="text-align: center"><strong>Binomial Tree</strong> </h2>
        """,
        unsafe_allow_html=True,
    )

    # -------------------------
    # Display binomial tree
    # -------------------------
    if tree_data is not None:
        st.markdown(
            f"""
            <div style="padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                <pre style="text-align: left;">{tree_data}</pre>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # -------------------------
    # idle state
    # -------------------------
    st.info("Binomial tree will be displayed here after computation.")