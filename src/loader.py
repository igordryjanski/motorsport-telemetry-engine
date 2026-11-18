from pathlib import Path
import numpy as np
import pandas as pd
import fastf1


def init_cache(cache_dir: str = "cache") -> None:
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)


def load_fastest_lap_telemetry(
    year: int, grand_prix: str, session_type: str, driver_code: str
) -> tuple[pd.DataFrame, float]:
    session = fastf1.get_session(year, grand_prix, session_type)
    session.load(telemetry=True, laps=True, weather=False, messages=False)

    lap = session.laps.pick_drivers(driver_code).pick_fastest()
    if lap is None or pd.isna(lap["LapTime"]):
        raise ValueError(f"No valid fastest lap found for {driver_code}.")

    lap_time_s = float(lap["LapTime"].total_seconds())
    tel = lap.get_telemetry().copy()

    # Convert units to strict SI
    time_s = tel["Time"].dt.total_seconds().to_numpy(dtype=float)
    time_s -= time_s[0]  # Zero-reference lap start

    dist_m = tel["Distance"].to_numpy(dtype=float)
    speed_ms = tel["Speed"].to_numpy(dtype=float) / 3.6
    throttle_pct = tel["Throttle"].to_numpy(dtype=float)

    # Normalize Brake channel (boolean in modern F1 feeds -> 0.0 or 100.0%)
    if tel["Brake"].dtype == bool:
        brake_pct = tel["Brake"].astype(float).to_numpy() * 100.0
    else:
        brake_pct = tel["Brake"].to_numpy(dtype=float)

    gear = tel["nGear"].to_numpy(dtype=float)
    x_m = tel["X"].to_numpy(dtype=float) / 10.0
    y_m = tel["Y"].to_numpy(dtype=float) / 10.0

    # Enforce strict spatial monotonicity for valid interpolation
    valid_mask = np.concatenate(([True], np.diff(dist_m) > 1e-4))

    sanitized = pd.DataFrame(
        {
            "Distance": dist_m[valid_mask],
            "Time": time_s[valid_mask],
            "Speed": speed_ms[valid_mask],
            "Throttle": throttle_pct[valid_mask],
            "Brake": brake_pct[valid_mask],
            "nGear": gear[valid_mask],
            "X": x_m[valid_mask],
            "Y": y_m[valid_mask],
        }
    )

    return sanitized, lap_time_s
