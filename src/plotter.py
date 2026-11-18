from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def _apply_dark_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#0E1117",
            "axes.facecolor": "#161B22",
            "axes.edgecolor": "#30363D",
            "axes.labelcolor": "#E6EDF3",
            "xtick.color": "#8B949E",
            "ytick.color": "#8B949E",
            "text.color": "#E6EDF3",
            "grid.color": "#21262D",
            "grid.linestyle": "--",
            "grid.linewidth": 0.7,
            "font.family": "sans-serif",
            "font.size": 10,
        }
    )


def plot_qualifying_comparison(
    aligned: pd.DataFrame,
    corners: pd.DataFrame,
    ref_label: str,
    comp_label: str,
    title: str,
    output_path: str,
) -> None:
    """Generate a 5-panel distance-aligned telemetry + g-load comparison figure."""
    _apply_dark_style()
    c_ref, c_comp = "#00D2BE", "#FF4B4B"

    fig, axes = plt.subplots(
        5,
        1,
        figsize=(15, 12.5),
        sharex=True,
        gridspec_kw={"height_ratios": [1.0, 2.0, 1.3, 1.1, 0.8], "hspace": 0.08},
    )

    s = aligned["Distance"]

    # Panel 1: Cumulative Time Delta
    ax0 = axes[0]
    ax0.axhline(0.0, color="#8B949E", linewidth=0.9, linestyle=":")
    ax0.plot(s, aligned["Delta_t"], color="#F0F6FC", linewidth=1.5)
    ax0.fill_between(s, 0, aligned["Delta_t"], where=(aligned["Delta_t"] >= 0), color=c_ref, alpha=0.20)
    ax0.fill_between(s, 0, aligned["Delta_t"], where=(aligned["Delta_t"] < 0), color=c_comp, alpha=0.20)
    ax0.set_ylabel(r"$\Delta t$ [s]")
    ax0.set_title(title, fontsize=13, fontweight="bold", pad=12, loc="left")
    ax0.grid(True)

    # Panel 2: Speed Trace + Detected Corner Markers
    ax1 = axes[1]
    ax1.plot(s, aligned["Speed_ref"] * 3.6, color=c_ref, linewidth=1.6, label=ref_label)
    ax1.plot(s, aligned["Speed_comp"] * 3.6, color=c_comp, linewidth=1.6, label=comp_label)
    for _, c_row in corners.iterrows():
        ax1.axvline(c_row["s_apex_ref"], color="#484F58", linewidth=0.7, linestyle=":")
        ax1.text(
            c_row["s_apex_ref"],
            ax1.get_ylim()[1] * 0.94 if ax1.get_ylim()[1] > 10 else 310,
            c_row["Corner"],
            color="#8B949E",
            fontsize=8,
            ha="center",
        )
    ax1.set_ylabel("Speed [km/h]")
    ax1.legend(loc="upper right", frameon=True, facecolor="#0E1117", edgecolor="#30363D")
    ax1.grid(True)

    # Panel 3: Longitudinal & Lateral G-Loads
    ax2 = axes[2]
    ax2.axhline(0.0, color="#484F58", linewidth=0.8)
    ax2.plot(s, aligned["Gx_ref"], color=c_ref, linewidth=1.2, label=r"$G_x$ (Longitudinal)")
    ax2.plot(s, aligned["Gx_comp"], color=c_comp, linewidth=1.2)
    ax2.plot(s, aligned["Gy_ref"], color=c_ref, linewidth=1.0, linestyle="--", alpha=0.75, label=r"$G_y$ (Lateral)")
    ax2.plot(s, aligned["Gy_comp"], color=c_comp, linewidth=1.0, linestyle="--", alpha=0.75)
    ax2.set_ylabel("Accel [g]")
    ax2.legend(loc="upper right", frameon=True, facecolor="#0E1117", edgecolor="#30363D", fontsize=8.5)
    ax2.grid(True)

    # Panel 4: Driver Inputs
    ax3 = axes[3]
    ax3.plot(s, aligned["Throttle_ref"], color=c_ref, linewidth=1.2, label="Throttle")
    ax3.plot(s, aligned["Throttle_comp"], color=c_comp, linewidth=1.2)
    ax3.plot(s, aligned["Brake_ref"], color=c_ref, linewidth=0.9, linestyle="--", alpha=0.75, label="Brake")
    ax3.plot(s, aligned["Brake_comp"], color=c_comp, linewidth=0.9, linestyle="--", alpha=0.75)
    ax3.set_ylabel("Inputs [%]")
    ax3.set_ylim(-5, 108)
    ax3.legend(loc="center right", frameon=True, facecolor="#0E1117", edgecolor="#30363D", fontsize=8.5)
    ax3.grid(True)

    # Panel 5: Gear
    ax4 = axes[4]
    ax4.step(s, aligned["Gear_ref"], where="mid", color=c_ref, linewidth=1.3)
    ax4.step(s, aligned["Gear_comp"], where="mid", color=c_comp, linewidth=1.3)
    ax4.set_ylabel("Gear [-]")
    ax4.set_xlabel("Track Distance $s$ [m]")
    ax4.set_yticks(range(1, 9))
    ax4.set_xlim(s.min(), s.max())
    ax4.grid(True)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_gg_and_track_dominance(
    aligned: pd.DataFrame,
    corners: pd.DataFrame,
    ref_label: str,
    comp_label: str,
    title: str,
    output_path: str,
) -> None:
    """Generate a 2-panel g-g traction circle & track dominance / corner map."""
    _apply_dark_style()
    c_ref, c_comp = "#00D2BE", "#FF4B4B"

    fig, (ax_gg, ax_map) = plt.subplots(1, 2, figsize=(15, 7))

    # Left Panel: g-g Traction Circle
    theta = np.linspace(0, 2 * np.pi, 360)
    for r in (1.0, 2.0, 3.0, 4.0, 5.0):
        ax_gg.plot(r * np.cos(theta), r * np.sin(theta), color="#30363D", linestyle=":", linewidth=0.8)
        ax_gg.text(0.08, r + 0.08, f"{r:.0f}g", color="#8B949E", fontsize=8)

    ax_gg.axhline(0, color="#484F58", linewidth=0.9)
    ax_gg.axvline(0, color="#484F58", linewidth=0.9)
    ax_gg.scatter(aligned["Gy_ref"], aligned["Gx_ref"], s=6, color=c_ref, alpha=0.55, label=ref_label)
    ax_gg.scatter(aligned["Gy_comp"], aligned["Gx_comp"], s=6, color=c_comp, alpha=0.55, label=comp_label)
    ax_gg.set_aspect("equal", adjustable="box")
    ax_gg.set_xlim(-6.0, 6.0)
    ax_gg.set_ylim(-6.0, 3.0)
    ax_gg.set_xlabel(r"Lateral Acceleration $G_y$ [g]  (Left $+$ / Right $-$)")
    ax_gg.set_ylabel(r"Longitudinal Acceleration $G_x$ [g]  (Accel $+$ / Brake $-$)")
    ax_gg.set_title("g-g Traction Envelope", fontsize=12, fontweight="bold")
    ax_gg.legend(loc="upper right", frameon=True, facecolor="#0E1117", edgecolor="#30363D")
    ax_gg.grid(True)

    # Right Panel: Track Dominance Map (colored by local d(Delta_t)/ds)
    dt_slope = np.gradient(aligned["Delta_t"], aligned["Distance"])
    faster_ref = dt_slope >= 0

    ax_map.scatter(
        aligned.loc[faster_ref, "X_ref"],
        aligned.loc[faster_ref, "Y_ref"],
        c=c_ref,
        s=8,
        label=f"{ref_label} faster sector",
    )
    ax_map.scatter(
        aligned.loc[~faster_ref, "X_ref"],
        aligned.loc[~faster_ref, "Y_ref"],
        c=c_comp,
        s=8,
        label=f"{comp_label} faster sector",
    )

    for _, c_row in corners.iterrows():
        idx = int((aligned["Distance"] - c_row["s_apex_ref"]).abs().idxmin())
        ax_map.text(
            aligned.loc[idx, "X_ref"],
            aligned.loc[idx, "Y_ref"],
            c_row["Corner"],
            color="#F0F6FC",
            fontsize=8.5,
            fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.18", facecolor="#0E1117", edgecolor="#30363D", alpha=0.85),
        )

    ax_map.set_aspect("equal", adjustable="box")
    ax_map.axis("off")
    ax_map.set_title("Track Dominance & Detected Corners", fontsize=12, fontweight="bold")
    ax_map.legend(loc="lower right", frameon=True, facecolor="#0E1117", edgecolor="#30363D")

    fig.suptitle(title, fontsize=14, fontweight="bold", y=0.98)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
#Made by Gemini
