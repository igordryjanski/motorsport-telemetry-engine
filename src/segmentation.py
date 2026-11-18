import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def detect_corner_phases(
    df: pd.DataFrame,
    kappa_threshold: float = 0.005,
    min_spacing_m: int = 110,
) -> pd.DataFrame:
    """
    Detect distinct corners from reference planar curvature peaks and extract
    braking point, apex (V_min), and full-throttle pickup for both drivers.
    """
    s = df["Distance"].to_numpy()
    kappa_abs = np.abs(df["kappa_ref"].to_numpy())

    # Identify major geometric corners (R <= 1 / kappa_threshold)
    peaks, _ = find_peaks(kappa_abs, height=kappa_threshold, distance=min_spacing_m)

    records = []
    for idx, p_idx in enumerate(peaks, start=1):
        s_peak = s[p_idx]
        # Search window: 140 m upstream of curvature peak to 90 m downstream
        i_start = max(0, p_idx - 140)
        i_end = min(len(s) - 1, p_idx + 90)

        row = {"Corner": f"C{idx}", "s_geom_m": float(s_peak)}

        for tag in ("ref", "comp"):
            v_win = df[f"Speed_{tag}"].to_numpy()[i_start : i_end + 1]
            s_win = s[i_start : i_end + 1]
            brake_win = df[f"Brake_{tag}"].to_numpy()[i_start : i_end + 1]
            throt_win = df[f"Throttle_{tag}"].to_numpy()[i_start : i_end + 1]

            # 1. Apex = minimum speed point in window
            apex_local = int(np.argmin(v_win))
            apex_global = i_start + apex_local
            v_apex_kmh = float(v_win[apex_local] * 3.6)
            s_apex = float(s_win[apex_local])

            # 2. Braking initiation = first brake >= 5% upstream of apex
            pre_brake = np.where(brake_win[: apex_local + 1] >= 5.0)[0]
            s_brake = float(s_win[pre_brake[0]]) if len(pre_brake) > 0 else np.nan

            # 3. Full-throttle pickup = first throttle >= 98% downstream of apex
            post_throt = np.where(throt_win[apex_local:] >= 98.0)[0]
            s_throt = float(s_win[apex_local + post_throt[0]]) if len(post_throt) > 0 else np.nan

            row[f"s_brake_{tag}"] = s_brake
            row[f"s_apex_{tag}"] = s_apex
            row[f"v_apex_kmh_{tag}"] = v_apex_kmh
            row[f"s_throt_{tag}"] = s_throt
            row[f"dt_exit_{tag}"] = float(df[f"Time_{tag}"].iloc[i_end] - df[f"Time_{tag}"].iloc[i_start])

        row["sector_delta_s"] = row["dt_exit_comp"] - row["dt_exit_ref"]
        row["dv_apex_kmh"] = row["v_apex_kmh_comp"] - row["v_apex_kmh_ref"]
        records.append(row)

    return pd.DataFrame(records)
