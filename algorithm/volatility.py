import numpy as np
import collections
from algorithm.pricing import np_price
from datetime import date, datetime
import streamlit as st
from scipy.interpolate import RBFInterpolator

from data.stock_option_chain_data import fetch_option_data


def crr_up_down(vol, dt):
    """
    Cox–Ross–Rubinstein up and down factors
    """
    u = np.exp(vol * np.sqrt(dt))
    d = 1 / u
    return u, d


class IVSurface:
    def __init__(self, ticker) -> None:
        self.ticker = ticker
        self.spot = None
        self.stock_option_chain_data = collections.defaultdict(dict)
        self.r = 0.04
        self.q = 0.00
        self.N = 1000
        self.iv_data_x = []
        self.iv_data_y = []
        self.iv_data_iv = []
        self.rbf = None

        stock_data = fetch_option_data()
        self.stock_option_chain_data = stock_data.get(ticker, {})

    def main_iv_runner(self):
        x, y, z = self.build_iv_points()
        self.rbf = self.build_rbf(x, y, z)
        XX, TT, IVgrid = self.get_grid_data(x, y, z)
        return (XX, TT, IVgrid), self.rbf

    def iv_newton_fd_binomial(
        self,
        option_price,
        S0,
        K,
        r,
        T,
        opttype,
        optclass="E",
        lo=0.01,
        hi=3.0,
        tol=1e-6,
        maxiter=30
    ):
        
        N = self.N
        dt = T / N

        def price(vol):
            u, d = crr_up_down(vol, dt)
            return np_price(S0, K, T, r, N, u, d, opttype=opttype, optclass=optclass)

        def f(vol):
            return price(vol) - option_price

        # bracket root
        try:
            f_lo = f(lo)
            f_hi = f(hi)

            if np.sign(f_lo) == np.sign(f_hi):
                for hi2 in (5.0, 8.0, 12.0):
                    f_hi2 = f(hi2)
                    if np.sign(f_lo) != np.sign(f_hi2):
                        hi, f_hi = hi2, f_hi2
                        break
                else:
                    return None  # never bracketed
        except Exception:
            return None

        # initial guess: midpoint
        vol = 0.5 * (lo + hi)

        for _ in range(maxiter):
            try:
                fv = f(vol)
            except Exception:
                vol = 0.5 * (lo + hi)
                continue

            if abs(fv) <= tol:
                return float(vol)

            # finite-difference vega (central difference)
            # vega = (f(vol + eps) - f(vol - eps)) / (2 * eps) but with dynamic eps based on vol level
            eps = max(1e-4, 1e-2 * vol)
            v1 = max(lo, vol - eps)
            v2 = min(hi, vol + eps)

            if v2 <= v1:
                vol = 0.5 * (lo + hi)
                continue

            try:
                f1 = f(v1)
                f2 = f(v2)
                vega = (f2 - f1) / (v2 - v1)
            except Exception:
                vol = 0.5 * (lo + hi)
                continue

            if not np.isfinite(vega) or abs(vega) < 1e-10:
                vol = 0.5 * (lo + hi)
            else:
                new_vol = vol - fv / vega
                if new_vol <= lo or new_vol >= hi or not np.isfinite(new_vol):
                    new_vol = 0.5 * (lo + hi)
                vol = new_vol

            try:
                fv = f(vol)
            except Exception:
                vol = 0.5 * (lo + hi)
                continue

            if np.sign(f_lo) == np.sign(fv):
                lo, f_lo = vol, fv
            else:
                hi, f_hi = vol, fv

            if (hi - lo) < 1e-8:
                return float(0.5 * (lo + hi))

        return None

    def build_iv_points_for_expiry(self, exp_date, now, mad_z=4.0, min_pts=6, atm_band=0.03):
        calls_df = self.stock_option_chain_data[exp_date].get("calls")
        puts_df = self.stock_option_chain_data[exp_date].get("puts")

        if calls_df is None or puts_df is None or len(calls_df) == 0 or len(puts_df) == 0:
            return

        if isinstance(exp_date, datetime):
            exp_date = exp_date.date()
        if isinstance(now, datetime):
            now = now.date()

        delta_days = (exp_date - now).days
        if delta_days <= 0:
            return
        T = float(np.round(delta_days / 365.25, 6))

        F = self.spot * np.exp((self.r - self.q) * T)
        local_x, local_iv = [], []

        # calls: ATM + OTM (moneyness >= -atm_band)
        for row in calls_df.itertuples(index=False):
            K = float(row.strike)
            mid_price = float(row.mid)
            moneyness = np.log(K / F)

            if moneyness < -atm_band or moneyness > 0.5 or mid_price <= 0:
                continue

            iv = self.iv_newton_fd_binomial(
                option_price=mid_price, S0=self.spot, K=K, r=self.r, T=T, opttype="C"
            )
            if iv is None or not (0.01 <= iv <= 1.1):
                continue

            local_x.append(moneyness)
            local_iv.append(iv)

        # puts: OTM + ATM (moneyness <= +atm_band)
        for row in puts_df.itertuples(index=False):
            K = float(row.strike)
            mid_price = float(row.mid)
            moneyness = np.log(K / F)

            if moneyness > atm_band or moneyness < -0.5 or mid_price <= 0:
                continue

            iv = self.iv_newton_fd_binomial(
                option_price=mid_price, S0=self.spot, K=K, r=self.r, T=T, opttype="P"
            )
            if iv is None or not (0.01 <= iv <= 1.1):
                continue

            local_x.append(moneyness)
            local_iv.append(iv)

        if len(local_x) < min_pts:
            return

        # MAD outlier filter per expiry slice
        ivs = np.array(local_iv)
        med = np.median(ivs)
        mad = np.median(np.abs(ivs - med))
        if mad > 0:
            mask = np.abs(ivs - med) / (1.4826 * mad) <= mad_z
        else:
            mask = np.ones(len(ivs), dtype=bool)

        if mask.sum() < min_pts:
            return

        for i, keep in enumerate(mask):
            if keep:
                self.iv_data_x.append(local_x[i])
                self.iv_data_y.append(T)
                self.iv_data_iv.append(local_iv[i])

    def build_iv_points(self):
        self.iv_data_x, self.iv_data_y, self.iv_data_iv = [], [], []

        if self.spot is None:
            from data.stock_option_chain_data import get_stock_price
            self.spot = get_stock_price(self.ticker)

        now = date.today()

        for exp in self.stock_option_chain_data.keys():
            if isinstance(exp, str):
                exp_date = date.fromisoformat(exp)
            elif isinstance(exp, datetime):
                exp_date = exp.date()
            else:
                exp_date = exp

            if exp_date <= now:
                continue

            self.build_iv_points_for_expiry(exp_date, now)

        if len(self.iv_data_x) == 0:
            raise ValueError("No IV points collected — check API data and filters")

        return (
            np.array(self.iv_data_x),
            np.array(self.iv_data_y),
            np.array(self.iv_data_iv),
        )

    def get_grid_data(self, x, T, iv, nx=60, nT=30):
        """
        Returns XX, TT, IVgrid (each shape: [nT, nx])
        """
        x_min, x_max = np.quantile(x, [0.02, 0.98])
        T_min, T_max = T.min(), T.max()

        xg = np.linspace(x_min, x_max, nx)
        Tg = np.linspace(T_min, T_max, nT)
        XX, TT = np.meshgrid(xg, Tg)

        rbf = self.rbf if self.rbf else self.build_rbf(x, T, iv)
        query_pts = np.column_stack([XX.ravel(), TT.ravel()])
        IVgrid = self.rbf(query_pts).reshape(XX.shape)

        return XX, TT, IVgrid

    def build_rbf(self, x, T, iv, rbf_smooth=0.02) -> RBFInterpolator:
        pts = np.column_stack([x, T])
        rbf = RBFInterpolator(
            pts, iv, kernel="multiquadric", epsilon=1.0, smoothing=rbf_smooth
        )
        self.rbf = rbf
        return rbf
