import argparse

from src.loader import init_cache, load_csv_telemetry, load_fastest_lap_telemetry
from src.physics import align_laps_by_distance, compute_kinematics
from src.segmentation import detect_corner_phases
from src.plotter import plot_qualifying_comparison, plot_gg_and_track_dominance


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Distance-aligned motorsport telemetry parser, kinematics & corner analyzer."
    )
    sub = parser.add_subparsers(dest="mode", required=True)

    p_f1 = sub.add_parser("fastf1", help="Compare fastest qualifying/race laps from FastF1.")
    p_f1.add_argument("--year", type=int, default=2024, help="Championship year (default: 2024)")
    p_f1.add_argument("--gp", default="Japan", help="Grand Prix name (default: Japan)")
    p_f1.add_argument("--session", default="Q", help="Session type: Q, R, FP1, SQ (default: Q)")
    p_f1.add_argument("--ref", default="VER", help="Reference driver 3-letter code (default: VER)")
    p_f1.add_argument("--comp", default="NOR", help="Comparison driver 3-letter code (default: NOR)")
    p_f1.add_argument("--ds", type=float, default=1.0, help="Spatial grid resolution in meters")

    p_csv = sub.add_parser("csv", help="Compare two local CSV telemetry logs (Formula Student / Sim).")
    p_csv.add_argument("--ref-csv", required=True, help="Path to reference lap CSV")
    p_csv.add_argument("--comp-csv", required=True, help="Path to comparison lap CSV")
    p_csv.add_argument("--ref-name", default="Run_A", help="Reference trace label")
    p_csv.add_argument("--comp-name", default="Run_B", help="Comparison trace label")
    p_csv.add_argument("--title", default="Formula Student Telemetry Comparison", help="Plot title")
    p_csv.add_argument("--ds", type=float, default=0.5, help="Spatial grid resolution in meters")
    p_csv.add_argument("--kappa-thresh", type=float, default=0.02, help="Corner curvature threshold [1/m]")
    p_csv.add_argument("--speed-unit", choices=("auto", "ms", "kmh"), default="auto", help="CSV Speed unit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "fastf1":
        init_cache("cache")
        ref_id, comp_id = args.ref.upper(), args.comp.upper()
        print(f"Loading {args.year} {args.gp} ({args.session}) telemetry: {ref_id} vs {comp_id}...")
        tel_ref, t_ref = load_fastest_lap_telemetry(args.year, args.gp, args.session, ref_id)
        tel_comp, t_comp = load_fastest_lap_telemetry(args.year, args.gp, args.session, comp_id)
        base = f"figures/{args.year}_{args.gp.lower()}_{args.session.lower()}_{ref_id}_vs_{comp_id}"
        title = f"{args.year} {args.gp} ({args.session}) — {ref_id} vs {comp_id} Spatial Telemetry"
        kappa_thresh = 0.005
    else:
        ref_id, comp_id = args.ref_name, args.comp_name
        print(f"Loading CSV telemetry: {args.ref_csv} vs {args.comp_csv}...")
        tel_ref, t_ref = load_csv_telemetry(args.ref_csv, speed_unit=args.speed_unit)
        tel_comp, t_comp = load_csv_telemetry(args.comp_csv, speed_unit=args.speed_unit)
        base = f"figures/csv_{ref_id.lower()}_vs_{comp_id.lower()}"
        title = args.title
        kappa_thresh = args.kappa_thresh

    aligned = align_laps_by_distance(tel_ref, tel_comp, ds=args.ds)
    kinematics = compute_kinematics(aligned, ds=args.ds)
    corners = detect_corner_phases(
        kinematics, kappa_threshold=kappa_thresh, min_spacing_m=max(1, int(60 / args.ds))
    )
    print(
        f"\n{ref_id} Lap: {t_ref:.3f} s | Max Lat: {kinematics['Gy_ref'].abs().max():.2f} g | "
        f"Max Brake: {kinematics['Gx_ref'].min():.2f} g"
    )
    print(
        f"{comp_id} Lap: {t_comp:.3f} s | Max Lat: {kinematics['Gy_comp'].abs().max():.2f} g | "
        f"Max Brake: {kinematics['Gx_comp'].min():.2f} g"
    )
    print(f"Official Gap: {t_comp - t_ref:+.3f} s | Integrated End Delta: {kinematics['Delta_t'].iloc[-1]:+.3f} s\n")

    if not corners.empty:
        cols = ["Corner", "s_apex_ref", "v_apex_kmh_ref", "v_apex_kmh_comp", "dv_apex_kmh", "sector_delta_s"]
        print("=== Automated Corner Phase Breakdown ===")
        print(corners[cols].to_string(index=False, float_format=lambda x: f"{x:+.2f}" if abs(x) < 15 else f"{x:.1f}"))

    plot_qualifying_comparison(
        aligned=kinematics,
        corners=corners,
        ref_label=f"{ref_id} ({t_ref:.3f}s)",
        comp_label=f"{comp_id} ({t_comp:.3f}s)",
        title=title,
        output_path=f"{base}_telemetry.png",
    )
    plot_gg_and_track_dominance(
        aligned=kinematics,
        corners=corners,
        ref_label=ref_id,
        comp_label=comp_id,
        title=f"{title} — Vehicle Dynamics",
        output_path=f"{base}_gg_dominance.png",
    )
    print(f"\nSaved figures:\n  - {base}_telemetry.png\n  - {base}_gg_dominance.png")


if __name__ == "__main__":
    main()
