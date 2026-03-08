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
]


@st.fragment
def price_output():
    price_data = st.session_state.get("option_price", None)

    if not price_data:
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

    call, put = price_data
    st.markdown(
        f"""
        <div class="term-panel">
            <div class="term-title">Option Price</div>
            <div class="term-row"><div class="term-k">Call</div><div class="term-v v-green">${call:,.3f}</div></div>
            <div class="term-row"><div class="term-k">Put</div><div class="term-v v-green">${put:,.3f}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

@st.fragment
def metrics_output():
    arb_data = st.session_state.get("arb_metrics")
    iv_value = st.session_state.get("iv_value")

    # Optional "running" flags (only if you have them)
    arb_running = st.session_state.get("arb_compute_on", False)
    iv_running  = st.session_state.get("iv_compute_on", False)

    if arb_running:
        pc_text, pc_cls = "—", "term-muted"   # or "Calculating..."
    elif isinstance(arb_data, dict) and arb_data.get("pc_parity") is not None:
        pc_text, pc_cls = str(arb_data["pc_parity"]), "v-blue"
    else:
        pc_text, pc_cls = "—", "term-muted"

    if iv_running:
        iv_text, iv_cls = "—", "term-muted"   # or "Calculating..."
    elif iv_value is not None:
        iv_pct = round(float(iv_value) * 100.0, 2)
        iv_text, iv_cls = f"{iv_pct}%", "v-blue"
    else:
        iv_text, iv_cls = "—", "term-muted"

    html = (
        '<div class="term-panel">'
            '<div class="term-title">Metrics</div>'

            '<div class="term-row">'
            '<div class="term-k">Put-Call Parity</div>'
                f'<div class="term-v {pc_cls}">{pc_text}</div>'
            '</div>'

            '<div class="term-row">'
            '<div class="term-k">Implied Volatility</div>'
                f'<div class="term-v {iv_cls}">{iv_text}</div>'
            '</div>'
        '</div>'
    )

    st.markdown(html, unsafe_allow_html=True)

@st.fragment
def greeks_output():
    greeks_dict = st.session_state.get("greeks", None)

    def get_val(name: str) -> tuple[float, float]:
        if not isinstance(greeks_dict, dict):
            return (0.0, 0.0)
        v = greeks_dict.get(name.lower(), None)
        if not isinstance(v, dict):
            return (0.0, 0.0)

        c = v.get("c", 0.0)
        p = v.get("p", 0.0)

        try:
            c = float(c)
        except Exception:
            c = 0.0
        try:
            p = float(p)
        except Exception:
            p = 0.0

        return (c, p)
    
    def tile(label: str, value: tuple):
        if value[0] == 0.0 and value[1] == 0.0:
            value_C = "-"
            value_P = "-"
            color = "term-v term-muted"
        else:
            value_C = np.round(value[0], 3)
            value_P = np.round(value[1], 3)
            color = "term-v v-blue"

        return (
            '<div class="term-tile" '
            'style="width:100%;aspect-ratio:1;display:flex;flex-direction:column;'
            'align-items:center;justify-content:flex-start;padding:12px;box-sizing:border-box;">'

                f'<div class="tile-label" style="text-align:center;margin-bottom:10px;">{label}</div>'

                '<div style="flex:1;width:100%;display:flex;flex-direction:column;'
                'align-items:center;justify-content:center;gap:8px;">'
                    f'<div class="{color}" style="text-align:center;">'
                        f'{value_C} <span style="font-size:0.8rem;color:red;">(C)</span>'
                    '</div>'

                    f'<div class="{color}" style="=text-align:center;">'
                        f'{value_P} <span style="font-size:0.8rem;color:red;">(P)</span>'
                    '</div>'
                '</div>'

            '</div>'
        )
        
    panel = st.container(border=False)
    with panel:
        c1, c2 = st.columns(2, gap="small")
        with c1: st.markdown(tile("Delta (Δ)", get_val("delta")), unsafe_allow_html=True)
        with c2: st.markdown(tile("Gamma (Γ)", get_val("gamma")), unsafe_allow_html=True)
        
        st.write("")
        
        c3, c4 = st.columns(2, gap="small")
        with c3: st.markdown(tile("Vega (ν)", (get_val("vega"))), unsafe_allow_html=True)
        with c4: st.markdown(tile("Theta (Θ)", get_val("theta")), unsafe_allow_html=True)

@st.fragment
def iv_graph_output():
    iv_compute_running = st.session_state.get("iv_compute_on", False)
    XX, TT, IVgrid = st.session_state.get("iv_data", (None, None, None))

    try:
        if IVgrid is None:
            st.markdown(
                f"""
            <div class="term-panel" style="min-height: full">
                <div class="term-title">Implied Volatility Surface</div>
                <div class="term-row"><div class="term-v term-muted">—</div></div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        else:
            fig = go.Figure(data=[go.Surface(x=XX, y=TT, z=IVgrid, showscale=True)])

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
                    aspectmode="cube",
                    xaxis=dict(color="white", gridcolor="rgba(255,255,255,0.2)"),
                    yaxis=dict(color="white", gridcolor="rgba(255,255,255,0.2)"),
                    zaxis=dict(color="white", gridcolor="rgba(255,255,255,0.2)"),
                    bgcolor="rgba(0,0,0,0)",
                ),
            )

            st.plotly_chart(
                fig,
                width="stretch",
                config={
                    "scrollZoom": True,
                    "displayModeBar": True,
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
