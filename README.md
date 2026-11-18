# Motorsport Telemetry Engine

A modular Python pipeline for distance-aligned Formula 1 telemetry analysis. It derives longitudinal and lateral acceleration, compares lap time deltas, detects corner phases, and creates telemetry and vehicle-dynamics plots.

## Requirements

- Python 3.10 or newer
- The packages listed in [`requirements.txt`](requirements.txt)
- An internet connection on the first run so FastF1 can retrieve session data

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

The current example analyzes the 2024 Japanese Grand Prix qualifying laps for VER and NOR. FastF1 stores downloaded session data in `cache/`; the cache is local and excluded from Git. The script prints a corner-phase summary and writes plots to `figures/`.

To change the season, event, session, or drivers, edit the settings near the start of `main()` in `main.py`.

## Project layout

- `src/loader.py` loads and normalizes FastF1 telemetry.
- `src/physics.py` aligns laps by distance and derives acceleration and time-delta channels.
- `src/segmentation.py` identifies corner phases.
- `src/plotter.py` generates the comparison plots.
- `data/` is reserved for optional project input data.
- `figures/` contains generated example plots.
