import streamlit as st
import plotly.graph_objects as go
import numpy as np

import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline, Rbf
import plotly.graph_objects as go

def smooth_smiles(x, T, iv, s_scale=0.002, mad_z=4.0, min_pts=6):
    """
    x: log-moneyness array
    T: year fraction array
    iv: implied vol array

    Returns: dataframe with columns [x, T, iv_raw, iv_smooth]
    """
    df = pd.DataFrame({"x": x, "T": T, "iv_raw": iv}).dropna()
    out = []

    for Tval, g in df.groupby("T"):
        g = g.sort_values("x").copy()
        if len(g) < min_pts:
            continue

        # MAD-based outlier filter (robust)
        med = g["iv_raw"].median()
        mad = (g["iv_raw"] - med).abs().median()
        if mad > 0:
            z = (g["iv_raw"] - med).abs() / (1.4826 * mad)
            g = g[z <= mad_z]
            if len(g) < min_pts:
                continue

        # Spline smoothing (tune s via s_scale)
        xs = g["x"].to_numpy()
        ys = g["iv_raw"].to_numpy()
        s = s_scale * len(g)  # bigger => smoother
        spl = UnivariateSpline(xs, ys, s=s)
        g["iv_smooth"] = spl(xs)

        out.append(g)

    return (
        pd.concat(out, ignore_index=True)
        if out
        else pd.DataFrame(columns=["x", "T", "iv_raw", "iv_smooth"])
    )

def build_surface_grid(df_s, nx=60, nT=30, rbf_smooth=0.002, exp_output=True):
    """
    df_s must contain columns x, T, iv_smooth
    Returns XX, TT, IVgrid (each shape: [nT, nx])
    """
    x_min, x_max = df_s["x"].quantile([0.02, 0.98]).to_numpy()
    T_min, T_max = df_s["T"].min(), df_s["T"].max()

    xg = np.linspace(x_min, x_max, nx)
    Tg = np.linspace(T_min, T_max, nT)
    XX, TT = np.meshgrid(xg, Tg)

    rbf = Rbf(
        df_s["x"].to_numpy(),
        df_s["T"].to_numpy(),
        df_s["iv_smooth"].to_numpy(),
        function="multiquadric",
        smooth=rbf_smooth,  # bigger => smoother
    )

    IVgrid = rbf(XX, TT)

    return XX, TT, IVgrid

@st.fragment
def iv_surface_plot(k, T, IV):
    df_s = smooth_smiles(k, T, IV, s_scale=0.003, mad_z=4.0)
    XX, TT, IVgrid = build_surface_grid(df_s, nx=70, nT=35, rbf_smooth=0.002)

    fig = go.Figure(
    data=[go.Surface(x=XX, y=TT, z=IVgrid, showscale=True)]
)

    SIDE = 650  # square size in px

    fig.update_layout(
        title="Implied Volatility Surface (RBF-smoothed)",
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
        use_container_width=False,
        config={
            "scrollZoom": False,
            "displayModeBar": False,
            "displaylogo": False,
            "responsive": False,
        },
    )