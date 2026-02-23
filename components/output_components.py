import streamlit as st
from algorithm.volatility import IVSurface
from scipy.interpolate import UnivariateSpline, Rbf
import plotly.graph_objects as go
import numpy as np
import pandas as pd

GREEKS = [
    ("Delta", "Δ"),
    ("Gamma", "Γ"),
    ("Theta", "Θ"),
    ("Vega", "ν"),
    ("Rho", "ρ"),
]


@st.fragment
def price_output():
    compute_on = st.session_state.get("price_compute_on", False)
    price_data = st.session_state.get("option_price", None)

    if not compute_on:
        st.markdown(
            """
            <div class="term-panel">
                <div class="term-title">Option Price</div>
                <div class="term-row"><div class="term-k">Call</div><div class="term-v term-muted">—</div></div>
                <div class="term-row"><div class="term-k">Put</div><div class="term-v term-muted">—</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if price_data is None:
        st.markdown(
            """
            <div class="term-panel">
                <div class="term-title">Option Price</div>
                <div class="term-row"><div class="term-k">Call</div><div class="term-v term-muted">Computing…</div></div>
                <div class="term-row"><div class="term-k">Put</div><div class="term-v term-muted">Computing…</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    call, put = price_data
    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-title">Option Price</div>
            <div class="term-row"><div class="term-k">Call</div><div class="term-v v-green">${call:,.4f}</div></div>
            <div class="term-row"><div class="term-k">Put</div><div class="term-v v-green">${put:,.4f}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.fragment
def arb_metrics_output():
    compute_on = st.session_state.get("price_compute_on", False)
    arb_data = st.session_state.get("arb_metrics", None)

    if not compute_on:
        st.markdown(
            """
            <div class="term-panel">
                <div class="term-title">Arbitrage Metrics</div>
                <div class="term-row"><div class="term-k">Put-Call Parity</div><div class="term-v term-muted">—</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    if arb_data is None:
        st.markdown(
            """
            <div class="term-panel">
                <div class="term-title">Arbitrage Metrics</div>
                <div class="term-row"><div class="term-k">Put-Call Parity</div><div class="term-v term-muted">Computing…</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-title">Arbitrage Metrics</div>
            <div class="term-row"><div class="term-k">Put-Call Parity</div><div class="term-v v-blue">{arb_data["pc_parity"]}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.fragment
def greeks_output():
    greeks_dict = st.session_state.get("greeks", None)

    html = '<div class="term-panel"><div class="term-title">Greeks</div><div class="tile-grid">'
    for name, symbol in GREEKS:
        if greeks_dict is None:
            val = "—"
        else:
            val = greeks_dict.get(name.lower(), "—")

        if isinstance(val, (int, float)):
            val = f"{val:.6f}"

        html += (
            f'<div class="term-tile">'
            f'  <div class="tile-label">{name} ({symbol})</div>'
            f'  <div class="tile-value">{val}</div>'
            f'</div>'
        )

    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)


@st.fragment
def iv_greeks_output():
    iv_value = st.session_state.get("iv_value", None)
    iv_value = np.round(iv_value, 4) if iv_value is not None else "—"
    iv_value = str(iv_value) if iv_value is not None else "—"

    XX, TT, IVgrid = st.session_state.get("iv_data", (None, None, None))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="term-panel" style="height: 100%; margin-bottom: 20px;">
                <div class="term-title">Implied Volatility</div>
                <div class="term-row"><div class="term-k">IV</div><div class="term-v v-red">{iv_value}</div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        greeks_output()
    with col2:
        try:
            fig = go.Figure(
                data=[go.Surface(x=XX, y=TT, z=IVgrid, showscale=True)]
            )

            SIDE = 650

            fig.update_layout(
            title="Implied Volatility Surface",
            width=SIDE,
            height=SIDE,
            margin=dict(l=0, r=0, t=40, b=0),
            scene=dict(
                xaxis_title="log-moneyness",
                yaxis_title="T (years)",
                zaxis_title="Implied Vol",
                aspectmode="cube",   # makes the 3D box feel “square/cubic”
            ),
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "scrollZoom": False,
                    "displayModeBar": False,
                    "displaylogo": False,
                    "responsive": False,
                },
            )
        except Exception as e:
            st.warning(f"Could not display IV surface: {e}")
            
@st.fragment
def binomial_tree_output():
    tree_data = st.session_state.get("binomial_tree", None)

    st.markdown(
        """
        <div class="term-panel">
            <div class="term-title">Binomial Tree</div>
        </div>
        """,
        unsafe_allow_html=True,
    )