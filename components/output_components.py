import streamlit as st
import plotly.graph_objects as go
import numpy as np

from algorithm.risk import pnl_summary
from algorithm.risk import pnl_scenario_matrix


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


def metrics_output():
    iv_value = st.session_state.get("iv_value")
    r_value  = st.session_state.get("risk_free_rate")

    iv_running = st.session_state.get("iv_compute_on", False)

    if iv_running:
        iv_text, iv_cls = "—", "term-muted"
    elif iv_value is not None:
        iv_pct = round(float(iv_value) * 100.0, 2)
        iv_text, iv_cls = f"{iv_pct}%", "v-blue"
    else:
        iv_text, iv_cls = "—", "term-muted"

    if r_value is not None:
        r_text, r_cls = f"{round(r_value * 100, 4)}%", "v-blue"
    else:
        r_text, r_cls = "—", "term-muted"


    html = (
        '<div class="term-panel">'
        '<div class="term-title">Metrics</div>'
        '<div class="term-row">'
        '<div class="term-k">Implied Volatility</div>'
        f'<div class="term-v {iv_cls}">{iv_text}</div>'
        "</div>"
        '<div class="term-row">'
        '<div class="term-k">Risk-Free Rate (r)</div>'
        f'<div class="term-v {r_cls}">{r_text}</div>'
        "</div>"
        "</div>"
    )

    st.markdown(html, unsafe_allow_html=True)


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
            '<div class="term-tile term-tile-layout">'
            f'<div class="term-title">{label}</div>'
            '<div class="term-tile-body">'
            f'<div class="{color} term-tile-value">'
            f'{value_C} <span class="term-tag">(C)</span>'
            "</div>"
            f'<div class="{color} term-tile-value">'
            f'{value_P} <span class="term-tag">(P)</span>'
            "</div>"
            "</div>"
            "</div>"
        )

    panel = st.container(border=False)
    with panel:
        c1, c2, c3, c4 = st.columns(4, gap="small")
        with c1:
            st.markdown(tile("Delta (Δ)", get_val("delta")), unsafe_allow_html=True)
        with c2:
            st.markdown(tile("Gamma (Γ)", get_val("gamma")), unsafe_allow_html=True)
        with c3:
            st.markdown(tile("Vega (ν)", get_val("vega")), unsafe_allow_html=True)
        with c4:
            st.markdown(tile("Theta (Θ)", get_val("theta")), unsafe_allow_html=True)


def pnl_summary_output() -> None:
    price_data = st.session_state.get("option_price")
    greeks_dict = st.session_state.get("greeks")

    if not price_data:
        st.markdown(
            '<div class="term-panel">'
            '<div class="term-row"><div class="term-v term-muted">—</div></div>'
            "</div>",
            unsafe_allow_html=True,
        )
        return

    call_price, put_price = price_data
    S0 = st.session_state.get("S0", 100)
    K = st.session_state.get("K", 100)
    T = st.session_state.get("T", 1.0)
    r = st.session_state.get("r", 0.04)
    vol = st.session_state.get("vol", 0.2)

    m = pnl_summary(S0, K, T, r, vol, call_price, put_price, greeks_dict)

    # ── Formatters ───────────────────────────────────────────────────

    def fmt_theta(val):
        if val is None:
            return "—"
        return f"${val:+,.2f}"

    def fmt_move(move_pct, already_itm):
        if already_itm:
            return "Already ITM"
        sign = "+" if move_pct >= 0 else ""
        return f"{sign}{move_pct:.2f}%"

    def fmt_moneyness(otm_pct):
        if abs(otm_pct) < 0.1:
            return "ATM"
        label = "OTM" if otm_pct > 0 else "ITM"
        return f"{abs(otm_pct):.2f}% {label}"

    
    # ── Days to expiry — shared header ───────────────────────────────

    dte_warning = " ⚠ Near expiry — some metrics suppressed" if m["near_expiry"] else ""
    st.markdown(
        '<div class="summary-tile" style="text-align:center;margin-bottom:10px">'
        '<div class="summary-tile-label">Days to Expiry</div>'
        f'<div class="summary-tile-value v-blue" style="font-size:1.75rem;">{m["days_to_expiry"]}'
        f'<span style="font-size:0.75rem;color:rgba(255,180,0,0.85)">{dte_warning}</span>'
        "</div>"
        "</div>",
        unsafe_allow_html=True
    )

    # ── Per-side columns ─────────────────────────────────────────────
    with st.popover("Metrics explained", use_container_width=True):
        st.markdown("P&L summary is per an option contract (100 shares). So metrics are a multiple of 100 to the single share values in the greek tiles.<br>Check the ? icons for more details on each metric.", unsafe_allow_html=True)

    HELPS = {
        "moneyness": "Whether the option is currently profitable to exercise. ITM = yes, OTM = not yet.",
        "max_loss": "The worst case outcome — you lose this if the option expires worthless.",
        "breakeven": "The stock price you need at expiry to just recover what you paid.",
        "move_req": "How much the stock still needs to move for this trade to become profitable (ITM).",
        "intrinsic": "What the option is worth right now if exercised immediately.",
        "time_val": "The extra premium you're paying for the chance the option improves before expiry.",
        "delta_hedge": "How many shares to hold to cancel out this option's directional exposure.",
        "theta_day": "How much value this option loses each day just from time passing.",
        "dollar_vega": "How much this option gains or loses if the market becomes 1% more volatile.",
        "premium_pos": "Total cost of your position across all contracts.",
        "hedge_pos": "Total shares needed to neutralise directional risk for this position.",
        "theta_pos": "Total daily value lost to time decay across your position.",
        "vega_pos": "Total exposure to a volatility shift across your position.",
    }

    def tile_with_help(label, value, cls, help_key, parent_col):
        """Render a CSS tile with a ghost st.metric alongside for the ? help icon."""
        tc, hc = parent_col.columns([9, 1])
        tc.markdown(
            f'<div class="summary-tile">'
            f'<div class="summary-tile-label">{label}</div>'
            f'<div class="summary-tile-value {cls}">{value}</div>'
            "</div>",
            unsafe_allow_html=True,
        )
        hc.metric("", "", help=HELPS[help_key])

    c_money = fmt_moneyness(m["call_otm_pct"])
    p_money = fmt_moneyness(m["put_otm_pct"])
    c_money_cls = "v-green" if m["call_already_itm"] else "v-blue"
    p_money_cls = "v-green" if m["put_already_itm"] else "v-blue"
    c_hedge = f"Sell {m['hedge_call']} sh" if m["hedge_call"] > 0 else "—"
    p_hedge = f"Buy {m['hedge_put']} sh" if m["hedge_put"] > 0 else "—"

    col_c, col_p = st.columns(2, gap="small")

    def render_col(
        col,
        header,
        money,
        money_cls,
        breakeven,
        be_move,
        intrinsic,
        time_val,
        max_loss,
        hedge,
        theta,
        vega,
    ):
        col.markdown(
            f'<div class="summary-col-header">{header}</div>', unsafe_allow_html=True
        )
        tile_with_help("Moneyness", money, money_cls, "moneyness", col)
        tile_with_help("Max Loss", f"${max_loss * 100:,.2f}", "v-red", "max_loss", col)
        tile_with_help("Breakeven", f"${breakeven:,.2f}", "v-blue", "breakeven", col)
        tile_with_help("Move Required", be_move, "v-blue", "move_req", col)
        tile_with_help(
            "Intrinsic Value", f"${intrinsic:,.2f}", "v-blue", "intrinsic", col
        )
        tile_with_help("Time Value", f"${time_val:,.2f}", "v-blue", "time_val", col)
        tile_with_help("Delta Hedge", hedge, "v-green", "delta_hedge", col)
        tile_with_help("Theta / Day", theta, "v-red", "theta_day", col)
        tile_with_help("Dollar Vega", vega, "v-yellow", "dollar_vega", col)

    render_col(
        col_c,
        "Call",
        money=c_money,
        money_cls=c_money_cls,
        breakeven=m["breakeven_call"],
        be_move=fmt_move(m["be_call_move_pct"], m["call_already_itm"]),
        intrinsic=m["intrinsic_call"],
        time_val=m["time_val_call"],
        max_loss=call_price,
        hedge=c_hedge,
        theta=fmt_theta(m["theta_day_call"]),
        vega=f"${m['dollar_vega_call']:,.2f}",
    )
    render_col(
        col_p,
        "Put",
        money=p_money,
        money_cls=p_money_cls,
        breakeven=m["breakeven_put"],
        be_move=fmt_move(m["be_put_move_pct"], m["put_already_itm"]),
        intrinsic=m["intrinsic_put"],
        time_val=m["time_val_put"],
        max_loss=put_price,
        hedge=p_hedge,
        theta=fmt_theta(m["theta_day_put"]),
        vega=f"${m['dollar_vega_put']:,.2f}",
    )

    # ── Position level ───────────────────────────────────────────────

    st.markdown(
        '<div class="term-title" style="font-size:0.8rem;margin-top:16px">Position</div>',
        unsafe_allow_html=True,
    )
    contracts = st.number_input(
        label="Number of option contracts in  position",
        min_value=1,
        max_value=10000,
        value=1,
        step=1,
    )

    pc1, pc2 = st.columns(2, gap="small")

    c_hedge_n = f"Sell {m['hedge_call'] * contracts} sh" if m["hedge_call"] > 0 else "—"
    p_hedge_n = f"Buy {m['hedge_put'] * contracts} sh" if m["hedge_put"] > 0 else "—"
    c_theta_pos = (
        m["theta_day_call"] * contracts if m["theta_day_call"] is not None else None
    )
    p_theta_pos = (
        m["theta_day_put"] * contracts if m["theta_day_put"] is not None else None
    )

    pc1.markdown('<div class="summary-col-header">Call</div>', unsafe_allow_html=True)
    tile_with_help(
        "Total Premium",
        f"${call_price * 100 * contracts:,.2f}",
        "v-blue",
        "premium_pos",
        pc1,
    )
    tile_with_help("Delta Hedge", c_hedge_n, "v-green", "hedge_pos", pc1)
    tile_with_help("Theta / Day", fmt_theta(c_theta_pos), "v-red", "theta_pos", pc1)
    tile_with_help(
        "Dollar Vega",
        f"${m['dollar_vega_call'] * contracts:,.2f}",
        "v-yellow",
        "vega_pos",
        pc1,
    )

    pc2.markdown('<div class="summary-col-header">Put</div>', unsafe_allow_html=True)
    tile_with_help(
        "Total Premium",
        f"${put_price * 100 * contracts:,.2f}",
        "v-blue",
        "premium_pos",
        pc2,
    )
    tile_with_help("Delta Hedge", p_hedge_n, "v-green", "hedge_pos", pc2)
    tile_with_help("Theta / Day", fmt_theta(p_theta_pos), "v-red", "theta_pos", pc2)
    tile_with_help(
        "Dollar Vega",
        f"${m['dollar_vega_put'] * contracts:,.2f}",
        "v-yellow",
        "vega_pos",
        pc2,
    )


def pnl_heatmap_output() -> None:
    price_data = st.session_state.get("option_price")
    if not price_data:
        st.markdown(
            '<div class="term-panel" style="min-height:120px">'
            '<div class="term-row"><div class="term-v term-muted">—</div></div>'
            "</div>",
            unsafe_allow_html=True,
        )
        return

    call_price, put_price = price_data
    S0 = st.session_state.get("S0", 100)
    K = st.session_state.get("K", 100)
    T = st.session_state.get("T", 1.0)
    r = st.session_state.get("r", 0.04)
    vol = st.session_state.get("vol", 0.2)
    optclass = st.session_state.get("optclass", "E")

    call_pnl, put_pnl, spot_shocks, vol_shocks = pnl_scenario_matrix(
        S0, K, T, r, vol, call_price, put_price, optclass
    )

    spot_labels = [
        "0%" if abs(s) < 1e-9 else f"{int(round(s * 100)):+d}%" for s in spot_shocks
    ]
    vol_labels = [
        "0%" if abs(v) < 1e-9 else f"{int(round(v * 100)):+d}%" for v in vol_shocks
    ]

    n_rows = len(vol_shocks)  # 7
    _margin = dict(l=60, r=95, t=50, b=60)
    _fig_height = n_rows * 95 + _margin["t"] + _margin["b"]

    _cfg = {
        "scrollZoom": False,
        "displayModeBar": False,
        "displaylogo": False,
        "responsive": True,
        "doubleClick": False,
        "showTips": False,
    }

    def _annotated_heatmap(matrix, title):
        # flip rows so +10pp vol is at top, -10pp at bottom
        matrix_display = matrix[::-1]
        vol_labels_display = vol_labels[::-1]

        text = [[f"${v:+.2f}" for v in row] for row in matrix_display]
        abs_max = max(abs(matrix_display.min()), abs(matrix_display.max()), 0.01)

        fig = go.Figure(
            go.Heatmap(
                z=matrix_display,
                x=spot_labels,
                y=vol_labels_display,
                text=text,
                texttemplate="%{text}",
                textfont=dict(size=11, color="rgba(0,0,0,0.85)"),
                colorscale="RdYlGn",
                zmin=-abs_max,
                zmax=abs_max,
                showscale=True,
                colorbar=dict(
                    tickfont=dict(color="rgba(255,255,255,0.7)", size=10),
                    title=dict(
                        text="P&L ($)",
                        font=dict(color="rgba(255,255,255,0.6)", size=10),
                    ),
                    thickness=14,
                ),
            )
        )
        fig.update_layout(
            title=title,
            height=_fig_height,
            margin=_margin,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.8)", size=11),
            dragmode=False,
            xaxis=dict(title="Spot shock", tickfont=dict(size=11), fixedrange=True),
            yaxis=dict(title="Vol shock", tickfont=dict(size=11), fixedrange=True),
        )
        return fig

    tab_call, tab_put = st.tabs(["Call P&L", "Put P&L"])
    with tab_call:
        st.plotly_chart(
            _annotated_heatmap(call_pnl, "Call P&L — Spot × Vol shocks"),
            width="stretch",
            config=_cfg,
        )
    with tab_put:
        st.plotly_chart(
            _annotated_heatmap(put_pnl, "Put P&L — Spot × Vol shocks"),
            width="stretch",
            config=_cfg,
        )


def iv_graph_output():
    XX, TT, IVgrid = st.session_state.get("iv_data", (None, None, None))

    try:
        if IVgrid is None:
            st.markdown(
                body=f"""
            <div class="term-panel">
                <div class="term-row"><div class="term-v term-muted">—</div></div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            fig = go.Figure(data=[go.Surface(x=XX, y=TT, z=IVgrid, showscale=True)])

            fig.update_layout(
                title=f"{st.session_state['stock_ticker']} (IV)",
                width=800,
                height=850,
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
