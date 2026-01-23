import streamlit as st

# CSS
CARD_CENTER = (
    "display: flex; flex-direction: column; align-items: center; "
    "justify-content: center; text-align: center; min-height: 5.5rem;"
)
LABEL = "font-size: 1.875rem; color: white;"
VALUE = (
    "font-size: 2.25rem; font-weight: 600; margin: 0.25rem 0 0 0; margin-bottom: 1rem; color: lightblue;"
    "line-height: 1.2;"
)
VALUE_READY = (
    "font-size: 2.25rem; font-weight: 700; margin: 0.25rem 0 0 0; margin-bottom: 1rem; color: green;"
    "letter-spacing: -0.02em; line-height: 1.2;"
)
MUTED = " color: var(--text-muted, #6b7280);"

GREEKS = [
    ("Delta", "Δ"),
    ("Gamma", "Γ"),
    ("Theta", "Θ"),
    ("Vega", "ν"),
    ("Rho", "ρ"),
]


@st.fragment
def price_output(price_data):
    with st.container(border=True):
        if not st.session_state.get("price_compute_on"):
            st.markdown(
                f'<div style="{CARD_CENTER}">'
                f'<span style="{LABEL}">Option Price</span>'
                f'<p style="{VALUE}{MUTED}">—</p></div>',
                unsafe_allow_html=True,
            )
            return
        if price_data is None:
            st.markdown(
                f'<div style="{CARD_CENTER}">'
                f'<span style="{LABEL}">Option Price</span>'
                f'<p style="{VALUE}{MUTED}">Computing…</p></div>',
                unsafe_allow_html=True,
            )
            return
        st.markdown(
            f'<div style="{CARD_CENTER}">'
            f'<span style="{LABEL}">Option Price</span>'
            f'<p style="{VALUE_READY}">${price_data["price"]:.4f}</p></div>',
            unsafe_allow_html=True,
        )


@st.fragment
def runtime_output(price_data):
    with st.container(border=True):
        if not st.session_state.get("price_compute_on"):
            st.markdown(
                f'<div style="{CARD_CENTER}">'
                f'<span style="{LABEL}">Runtime</span>'
                f'<p style="{VALUE}{MUTED}">—</p></div>',
                unsafe_allow_html=True,
            )
            return
        if price_data is None:
            st.markdown(
                f'<div style="{CARD_CENTER}">'
                f'<span style="{LABEL}">Runtime</span>'
                f'<p style="{VALUE}{MUTED}">Computing…</p></div>',
                unsafe_allow_html=True,
            )
            return
        rt = st.session_state.get("runtime", 0)
        st.markdown(
            f'<div style="{CARD_CENTER}">'
            f'<span style="{LABEL}">Runtime</span>'
            f'<p style="{VALUE}">{rt:.2f} s</p></div>',
            unsafe_allow_html=True,
        )


@st.fragment
def greeks_output(price_data):
    cols = st.columns(5)
    for i, (name, symbol) in enumerate(GREEKS):
        with cols[i]:
            with st.container(border=True):
                st.metric(f"{name} ({symbol})", "—")


@st.fragment
def binomial_tree_output(tree_data):
    with st.container(border=True):
        st.caption("Binomial Tree")
        if tree_data is not None:
            st.code(tree_data, language=None)
        else:
            st.text("—")
