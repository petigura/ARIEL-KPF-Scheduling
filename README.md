# ARIEL-KPF Scheduling Tool

A Python-based tool for generating observing blocks (OBs) and scheduling targets for the Keck Planet Finder (KPF) instrument at Keck Observatory. This tool processes ARIEL target data and creates properly formatted JSON files for submission to Keck Observatory.

## Overview

This tool automates the generation of observing blocks for ARIEL targets observable from Keck Observatory. The observing strategy is to obtain **four RVs of each target within a month-long observing window**.

## Repository Structure

```
ARIEL-KPF-Scheduling/
├── ariel_kpf/                    # Python package
│   ├── __init__.py               # Package initialization
│   └── paths.py                  # Centralized path management
├── bin/                          # Python scripts
│   ├── generate_obs.py           # Generate observation blocks for nov/dec/jan
│   ├── plot_november_airmass.py  # Plot airmass for November targets
│   ├── plot_november_targets.py  # Plot sky distribution
│   ├── create_kpf_targets.py     # Filter KPF targets from full dataset
│   └── download_ariel_data.py    # Download target data from Google Sheets
├── obs/                          # Observing blocks
│   ├── ob-template.json          # OB template with annotations
│   └── obs_*.json                # Generated observation files (gitignored)
├── targets/                      # Target data files
│   └── *.csv                     # Downloaded and generated target files
├── plots/                        # Generated plots (gitignored)
├── environment.yml               # Conda environment specification
├── setup.py                      # Package installation configuration
├── project-description.txt       # Project requirements and guidelines
└── README.md                     # This file
```

## Setup Instructions

### 1. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate ariel-rv
```

### 2. Install Package
```bash
pip install -e .
```

This installs the `ariel_kpf` package in development mode, which provides:
- Centralized path management (scripts work from any directory)
- Automatic discovery of latest target files
- Consistent data directory handling


## Usage

**Note:** After package installation, all scripts can be run from any directory. The package automatically finds the correct data directories.

### Download Latest Target Data

```bash
python bin/download_ariel_data.py
```

Downloads fresh target data from Google Sheets. Saves timestamped CSV files to `targets/` directory.

### Filter KPF Targets

```bash
python bin/create_kpf_targets.py
```

Filters KPF targets from the full ARIEL dataset and queries SIMBAD to populate target metadata. This step:
- Automatically uses the most recent downloaded file
- **Queries SIMBAD in batches** for all KPF targets (~50 targets per batch)
- Adds the following columns to the CSV:
  - `gaia_dr3_id`, `twomass_id` (identifiers)
  - `parallax`, `pmra`, `pmdec` (astrometry)
  - `gmag`, `jmag` (photometry)
  - `rv_value`, `sp_type` (physical properties)
- Saves timestamped CSV with all data included

**Note:** This step may take several minutes due to SIMBAD queries (~71 targets × ~0.5s per batch). Results are saved in the CSV, so subsequent operations are fast.

### Generate Observing Blocks

```bash
# Generate all months using default strategy (version1)
python bin/generate_obs.py

# Explicitly specify strategy version
python bin/generate_obs.py --strategy version1

# Short form with custom number of test targets
python bin/generate_obs.py -s version1 -t 5
```

**Strategy Versions:**
- `version1` (default): November (20-24h), December (0-4h), January (4-8h)

This will:
- Process all months defined in the strategy (November, December, January)
- Filter targets by each month's RA range
- Automatically use the most recent KPF targets file (with SIMBAD data)
- Populate observation blocks with target metadata from the CSV:
  - Gaia DR3 ID, 2MASS ID
  - Parallax, proper motions (PMRA, PMDEC)
  - Photometry (Gmag, Jmag)
  - Radial velocity, spectral type (if available)
- Generate OBs with appropriate observation windows for each month
- Create three output files:
  - `obs/obs_<strategy>.json` - All targets from all months (e.g., `obs_version1.json`)
  - `obs/obs_<strategy>_test.json` - First and last targets (2 OBs for quick testing)
  - `obs/obs_<strategy>_test20.json` - First 10 and last 10 targets (20 OBs for extended testing)
- **Automatically generate plots** showing:
  - Target distribution across the sky for all months
  - Brightness (V-mag) distribution
  - Airmass curves for each month's targets

**Note:** This step is fast since SIMBAD data is already in the CSV from the `create_kpf_targets.py` step.

**Generated plots** (automatically created in `plots/` directory):
- `<strategy>_target_distribution.png` - Sky distribution for all months with color-coding
- `<strategy>_airmass.png` - Airmass curves for all months' targets

### Manual Plotting (Optional)

If you want to generate plots independently or customize them, legacy plotting scripts are available:

```bash
python bin/plot_november_targets.py  # November-specific plots
python bin/plot_november_airmass.py  # November airmass curves
```

**Note:** These scripts are kept for backwards compatibility but plotting is now automatic when running `generate_obs.py`.

## Features

- **Centralized Path Management**: All data directories are managed by the `ariel_kpf` package, so scripts work from any directory
- **Automatic File Discovery**: Scripts automatically find and use the most recent target files
- **Multi-Month Support**: Generate observations for November, December, and January with appropriate RA ranges
- **Strategy Versioning**: Support for multiple observing strategies with version tags, enabling A/B testing and strategy evolution
- **SIMBAD Integration**: Bulk queries SIMBAD during target filtering to populate metadata (Gaia IDs, parallax, proper motions, magnitudes) in the CSV, making downstream operations fast
- **Automatic Plotting**: Generates visualization plots automatically showing target distribution and airmass curves for all months
- **Modular Design**: Plotting functions are separated into a dedicated module (`ariel_kpf/plotting.py`) for easy reuse and customization
- **Flexible Configuration**: Easy to add new strategy versions or modify RA ranges, observation windows, and other parameters
