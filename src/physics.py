import numpy as np
import pandas as pd
from scipy.signal import savgol_filter

G0 = 9.80665


def align_laps_by_distance(
    tel_ref: pd.DataFrame, tel_comp: pd.DataFrame, ds: float = 1.0
) -> pd.DataFrame:

    s_min = max(tel_ref["Distance"].min(), tel_comp["Distance"].min())
    s_max = min(tel_ref["Distance"].max(), tel_comp["Distance"].max())
    s_grid = np.arange(np.ceil(s_min), np.floor(s_max), ds)

    def interp_channel(df: pd.DataFrame, col: str) -> np.ndarray:
        return np.interp(s_grid, df["Distance"].to_numpy(), df[col].to_numpy())

    t_ref = interp_channel(tel_ref, "Time")
    t_comp = interp_channel(tel_comp, "Time")

    return pd.DataFrame(
        {
            "Distance": s_grid,
            "Time_ref": t_ref,
            "Time_comp": t_comp,
            "Delta_t": t_comp - t_ref,
            "Speed_ref": interp_channel(tel_ref, "Speed"),
            "Speed_comp": interp_channel(tel_comp, "Speed"),
            "Throttle_ref": interp_channel(tel_ref, "Throttle"),
            "Throttle_comp": interp_channel(tel_comp, "Throttle"),
            "Brake_ref": interp_channel(tel_ref, "Brake"),
            "Brake_comp": interp_channel(tel_comp, "Brake"),
            "Gear_ref": np.round(interp_channel(tel_ref, "nGear")),
            "Gear_comp": np.round(interp_channel(tel_comp, "nGear")),
            "X_ref": interp_channel(tel_ref, "X"),
            "Y_ref": interp_channel(tel_ref, "Y"),
            "X_comp": interp_channel(tel_comp, "X"),
            "Y_comp": interp_channel(tel_comp, "Y"),
        }
    )


def compute_kinematics(aligned: pd.DataFrame, ds: float = 1.0) -> pd.DataFrame:
    """
    Derive longitudinal acceleration (a_x = v * dv/ds), signed planar track
    curvature kappa(s), lateral acceleration (a_y = v^2 * kappa), and g-loads.
    """
    df = aligned.copy()
    v_win = 15    # 15 m smoothing window for velocity differentiation
    xy_win = 35   # 35 m window to suppress GPS quantization in 2nd derivatives

    for tag in ("ref", "comp"):
        v_raw = df[f"Speed_{tag}"].to_numpy()
        x_raw = df[f"X_{tag}"].to_numpy()
        y_raw = df[f"Y_{tag}"].to_numpy()

        v_smooth = savgol_filter(v_raw, window_length=v_win, polyorder=3)
        dv_ds = savgol_filter(v_raw, window_length=v_win, polyorder=3, deriv=1, delta=ds)
        ax = v_smooth * dv_ds

        dx = savgol_filter(x_raw, window_length=xy_win, polyorder=3, deriv=1, delta=ds)
        dy = savgol_filter(y_raw, window_length=xy_win, polyorder=3, deriv=1, delta=ds)
        ddx = savgol_filter(x_raw, window_length=xy_win, polyorder=3, deriv=2, delta=ds)
        ddy = savgol_filter(y_raw, window_length=xy_win, polyorder=3, deriv=2, delta=ds)

        denom = np.power(dx**2 + dy**2, 1.5)
        kappa = np.where(denom > 1e-6, (dx * ddy - dy * ddx) / denom, 0.0)
        ay = (v_smooth**2) * kappa

        gx = ax / G0
        gy = ay / G0
        g_comb = np.hypot(gx, gy)

        df[f"ax_{tag}"] = ax
        df[f"ay_{tag}"] = ay
        df[f"kappa_{tag}"] = kappa
        df[f"Gx_{tag}"] = gx
        df[f"Gy_{tag}"] = gy
        df[f"G_comb_{tag}"] = g_comb

    return df
