import numpy as np
import collections
from .pricing import np_price
from functools import lru_cache
import pandas as pd
from scipy.optimize import brentq
from datetime import datetime, timezone
import streamlit as st
from scipy.interpolate import UnivariateSpline, Rbf
import plotly.graph_objects as go


def crr_up_down(vol, dt):
    """
    Cox–Ross–Rubinstein up and down factors
    """

    u = np.exp(vol * np.sqrt(dt))
    d = 1 / u
    return u, d


class IVSurface:
    def __init__(self, ticker):
        self.ticker = ticker
        self.spot = None
        self.stock_option_chain_data = collections.defaultdict(dict)
        self.r = 0.04
        self.q = 0.00
        self.N = 1000
        self.iv_data_x = []
        self.iv_data_y = []
        self.iv_data_iv = []
        self.testing = True
        self.rbf = None

        # Extract data for the specific ticker: stock_data[ticker] = {exp_str: {calls/puts: df}}
        stock_data = st.session_state.get("stock_data", {})
        self.stock_option_chain_data = stock_data.get(ticker, {})

    def main_iv_runner(self, today=datetime.now(timezone.utc).today().day):
        x, y, z = self.build_iv_points()
        df_s = self.smooth_smiles(x, y, z)
        self.build_rbf(df_s) if not self.rbf else self.rbf

        XX, TT, IVgrid = self.get_grid_data(df_s)
        return (XX, TT, IVgrid), self.rbf

    def iv_brentq_binomial(self, option_price, S0, K, r, T, opttype):
        N = self.N
        dt = T / N

        def objective(vol):
            u, d = crr_up_down(vol, dt)
            # if your binomial pricer supports q, use r - q in p / discounting
            model_price = np_price(S0, K, T, r, N, u, d, opttype)
            return model_price - option_price

        lo, hi = 0.01, 3.0
        try:
            f_lo = objective(lo)
            f_hi = objective(hi)

            # try expanding the upper bound if we didn't bracket a root
            if np.sign(f_lo) == np.sign(f_hi):
                for hi in (5.0, 8.0, 12.0):
                    f_hi = objective(hi)
                    if np.sign(f_lo) != np.sign(f_hi):
                        break
                else:
                    return None  # never bracketed

            return float(brentq(objective, lo, hi, xtol=1e-6, maxiter=200))
        except Exception:
            return None

    def _filter_chain(self, df):
        """Liquidity + sanity filters; returns copy with mid/spread_pct"""
        if df is None or len(df) == 0:
            return df

        d = df.copy()

        d["mid"] = (d["bid"] + d["ask"]) / 2
        d = d[d["mid"] > 0.01]

        # your liquidity filters
        d = d[(d["lastPrice"] > 0.10) & (d["volume"] > 10) & (d["openInterest"] > 50)]

        d["spread"] = d["ask"] - d["bid"]
        d["spread_pct"] = d["spread"] / d["mid"]
        d = d[d["spread_pct"] <= 0.30]  # 30% max spread

        return d

    def build_iv_points_otm_for_expiry(self, exp_str, exp_date, now):
        calls_df = self._filter_chain(
            self.stock_option_chain_data[exp_str].get("calls")
        )
        puts_df = self._filter_chain(
            self.stock_option_chain_data[exp_str].get("puts")
        )

        if (
            calls_df is None
            or puts_df is None
            or len(calls_df) == 0
            or len(puts_df) == 0
        ):
            raise ValueError

        T = (exp_date - now).total_seconds() / (60 * 60 * 24 * 365.25)
        T = float(np.round(T, 6))

        if T < 14 / 365:
            return

        # ---- OTM CALLS (K > spot) ----
        otm_calls = calls_df[calls_df["strike"] > self.spot]
        for row in otm_calls.itertuples(index=False):
            K = float(row.strike)
            mid_price = float(row.mid)
            F = self.spot * np.exp((self.r - self.q) * T)
            moneyness = np.log(K / F)  # log-moneyness for calls
            if moneyness > 0.5 or moneyness < -0.5:
                continue  # skip very deep ITM/OTM calls

            iv = self.iv_brentq_binomial(
                option_price=mid_price, S0=self.spot, K=K, r=self.r, T=T, opttype="C"
            )
            if iv is None or not (0.03 <= iv <= 0.95):
                continue

            self.iv_data_x.append(moneyness)  # or K/self.spot if you prefer moneyness
            self.iv_data_y.append(T)
            self.iv_data_iv.append(iv)

        # ---- OTM PUTS (K < spot) ----
        otm_puts = puts_df[puts_df["strike"] < self.spot]
        for row in otm_puts.itertuples(index=False):
            K = float(row.strike)
            mid_price = float(row.mid)
            F = self.spot * np.exp((self.r - self.q) * T)
            moneyness = np.log(K / F)  # log-moneyness for puts
            if moneyness > 0.5 or moneyness < -0.5:
                continue  # skip very deep ITM/OTM puts

            iv = self.iv_brentq_binomial(
                option_price=mid_price, S0=self.spot, K=K, r=self.r, T=T, opttype="P"
            )
            if iv is None or not (0.03 <= iv <= 0.95):
                continue

            self.iv_data_x.append(moneyness)  # or K/self.spot
            self.iv_data_y.append(T)
            self.iv_data_iv.append(iv)

    def build_iv_points(self):
        # reset so repeated calls don’t duplicate points
        self.iv_data_x, self.iv_data_y, self.iv_data_iv = [], [], []

        if self.spot is None:
            import yfinance as yf

            self.spot = float(
                yf.Ticker(self.ticker).history(period="1d")["Close"].iloc[-1]
            )

        now = datetime.now(timezone.utc)

        for exp_str in self.stock_option_chain_data.keys():
            exp_date = datetime.strptime(exp_str, "%Y-%m-%d").replace(
                tzinfo=timezone.utc
            )
            if exp_date <= now:
                continue
            self.build_iv_points_otm_for_expiry(exp_str, exp_date, now)

        return (
            np.array(self.iv_data_x),
            np.array(self.iv_data_y),
            np.array(self.iv_data_iv),
        )

    def smooth_smiles(self, x, T, iv, s_scale=0.002, mad_z=4.0, min_pts=6):
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

    def get_grid_data(self, df_s, nx=60, nT=30, rbf_smooth=0.002, exp_output=True):
        """
        df_s must contain columns x, T, iv_smooth
        Returns XX, TT, IVgrid (each shape: [nT, nx])
        """
        x_min, x_max = df_s["x"].quantile([0.02, 0.98]).to_numpy()
        T_min, T_max = df_s["T"].min(), df_s["T"].max()

        xg = np.linspace(x_min, x_max, nx)
        Tg = np.linspace(T_min, T_max, nT)
        XX, TT = np.meshgrid(xg, Tg)

        rbf = self.rbf if self.rbf else self.build_rbf(df_s)
        IVgrid = self.rbf(XX, TT)

        return XX, TT, IVgrid

    def build_rbf(self, df_s, rbf_smooth=0.002):
        """
        df_s must contain columns x, T, iv_smooth
        Builds the RBF interpolator and stores it in self.rbf
        """
        rbf = Rbf(
            df_s["x"].to_numpy(),
            df_s["T"].to_numpy(),
            df_s["iv_smooth"].to_numpy(),
            function="multiquadric",
            smooth=rbf_smooth,
        )

        self.rbf = rbf
