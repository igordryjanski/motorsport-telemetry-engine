# Motorsport Telemetry Engine

A modular Python telemetry ingestion, vehicle dynamics, and corner analysis pipeline for Formula 1 (`FastF1`) and Formula Student CSV logs, including MoTeC i2, AiM RaceStudio, and simulation exports.

## Capabilities

- Aligns asynchronous telemetry on a uniform arc-length grid and calculates cumulative lap time delta, `Δt(s) = t_comp(s) − t_ref(s)`.
- Derives longitudinal acceleration, signed track curvature, lateral acceleration, and g-g telemetry using Savitzky–Golay differentiation.
- Segments corners to estimate braking initiation, apex speed, throttle pickup, and time delta by corner.
- Ingests FastF1 data or generic CSV data with `Distance`, `Time`, and `Speed` columns. Optional columns are `Throttle`, `Brake`, `nGear`, `X`, and `Y`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Compare Formula 1 laps

```bash
python main.py fastf1 --year 2024 --gp Japan --session Q --ref VER --comp NOR
```

### Compare Formula Student CSV logs

```bash
python main.py csv \
  --ref-csv data/fs_autocross_ref.csv \
  --comp-csv data/fs_autocross_comp.csv \
  --ref-name Aero_Pkg_v2 \
  --comp-name Baseline \
  --title "FS Autocross Aero Package Comparison"
```

CSV speed units default to automatic detection (`>45` is interpreted as km/h). Set `--speed-unit ms` or `--speed-unit kmh` when the unit is known. The CSV loader expects distance in meters and time in seconds. Brake values are scaled to a 0–100 range when present.

The CSV command writes telemetry and g-g figures under `figures/`. FastF1 downloads are cached locally under `cache/`.

## Repository layout

```text
motorsport-telemetry-engine/
├── cache/                 # Local FastF1 cache (gitignored)
├── data/                  # CSV logs and demo fixtures
├── figures/               # Generated telemetry and g-g plots
├── src/
│   ├── loader.py          # FastF1 and CSV ingestion with SI normalization
│   ├── physics.py         # Spatial alignment and kinematic calculations
│   ├── segmentation.py    # Corner phase detection
│   └── plotter.py         # Telemetry and g-g plots
└── main.py                # CLI entry point
```
