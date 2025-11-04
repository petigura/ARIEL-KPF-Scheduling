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

Filters KPF targets from the full ARIEL dataset. Automatically uses the most recent downloaded file.

### Generate Observing Blocks

```bash
# Generate November observations (RA 20-24 hr, 300-360°)
python bin/generate_obs.py --month nov

# Generate December observations (RA 0-4 hr, 0-60°)
python bin/generate_obs.py --month dec

# Generate January observations (RA 4-8 hr, 60-120°)
python bin/generate_obs.py --month jan

# With custom number of test targets
python bin/generate_obs.py --month nov --test-targets 5
```

This will:
- Filter targets by the specified month's RA range
- Automatically use the most recent KPF targets file
- Generate OBs with appropriate observation windows
- Create two output files:
  - `obs/obs_{month}_2025.json` - All targets for that month
  - `obs/obs_{month}_2025_test.json` - First 2 targets (for testing upload)

### Plot November Target Distribution

```bash
python bin/plot_november_targets.py
```

Generates `plots/november_targets_context.png` showing:
- November targets (RA 20-24hr) highlighted in context
- All KPF targets for reference
- Color-coded by V-magnitude

### Plot Airmass for November Targets

```bash
python bin/plot_november_airmass.py
```

Generates `plots/november_airmass_all.png` showing:
- Airmass curves for all November targets
- Centered on midnight Hawaii local time
- Annotated with target names
- Day/night shading using `astroplan`

## Features

- **Centralized Path Management**: All data directories are managed by the `ariel_kpf` package, so scripts work from any directory
- **Automatic File Discovery**: Scripts automatically find and use the most recent target files
- **Multi-Month Support**: Generate observations for November, December, and January with appropriate RA ranges
- **Flexible Configuration**: Easy to modify RA ranges, observation windows, and other parameters in the `generate_obs.py` script
