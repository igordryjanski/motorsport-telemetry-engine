from src.loader import init_cache, load_fastest_lap_telemetry
from src.physics import align_laps_by_distance, compute_kinematics
from src.segmentation import detect_corner_phases
from src.plotter import plot_qualifying_comparison, plot_gg_and_track_dominance


def main() -> None:
    init_cache("cache")

    year = 2024
    gp = "Japan"
    session_type = "Q"
    ref_driver = "VER"
    comp_driver = "NOR"

    print(f"Loading {year} {gp} ({session_type}) telemetry for {ref_driver} vs {comp_driver}...")
    tel_ref, t_ref = load_fastest_lap_telemetry(year, gp, session_type, ref_driver)
    tel_comp, t_comp = load_fastest_lap_telemetry(year, gp, session_type, comp_driver)

    aligned = align_laps_by_distance(tel_ref, tel_comp, ds=1.0)
    kinematics = compute_kinematics(aligned, ds=1.0)
    corners = detect_corner_phases(kinematics)

    print(f"\n{ref_driver} Pole Lap: {t_ref:.3f} s | Max Lateral: {kinematics['Gy_ref'].abs().max():.2f} g | Max Braking: {kinematics['Gx_ref'].min():.2f} g")
    print(f"{comp_driver} Best Lap: {t_comp:.3f} s | Max Lateral: {kinematics['Gy_comp'].abs().max():.2f} g | Max Braking: {kinematics['Gx_comp'].min():.2f} g")
    print(f"Official Gap:     {t_comp - t_ref:+.3f} s | Integrated End Delta: {kinematics['Delta_t'].iloc[-1]:+.3f} s\n")

    cols = ["Corner", "s_apex_ref", "v_apex_kmh_ref", "v_apex_kmh_comp", "dv_apex_kmh", "sector_delta_s"]
    print("=== Automated Corner Phase Breakdown ===")
    print(corners[cols].to_string(index=False, float_format=lambda x: f"{x:+.2f}" if abs(x) < 15 else f"{x:.1f}"))

    base = f"figures/{year}_{gp.lower()}_{ref_driver}_vs_{comp_driver}"
    plot_qualifying_comparison(
        aligned=kinematics,
        corners=corners,
        ref_label=f"{ref_driver} ({t_ref:.3f}s)",
        comp_label=f"{comp_driver} ({t_comp:.3f}s)",
        title=f"{year} Japanese GP Qualifying — {ref_driver} vs {comp_driver} Spatial Telemetry",
        output_path=f"{base}_telemetry.png",
    )
    plot_gg_and_track_dominance(
        aligned=kinematics,
        corners=corners,
        ref_label=ref_driver,
        comp_label=comp_driver,
        title=f"{year} Japanese GP Qualifying — {ref_driver} vs {comp_driver} Vehicle Dynamics",
        output_path=f"{base}_gg_dominance.png",
    )
    print(f"\nSaved figures:\n  - {base}_telemetry.png\n  - {base}_gg_dominance.png")


if __name__ == "__main__":
    main()
