# ARIEL-KPF Scheduling Tool

A Python-based tool for generating observing blocks (OBs) and scheduling targets for the Keck Planet Finder (KPF) instrument at Keck Observatory. This tool processes ARIEL target data and creates properly formatted JSON files for submission to Keck Observatory.

## Overview

This tool automates the generation of observing blocks for ARIEL targets observable from Keck Observatory. The observing strategy is to obtain **four RVs of each target within a month-long observing window**.

## Repository Structure

```
ARIEL-KPF-Scheduling/
├── bin/                          # Python scripts
│   ├── generate_obs_november.py  # Generate November 2025 OBs
│   ├── plot_november_airmass.py  # Plot airmass for November targets
│   ├── plot_november_targets.py  # Plot sky distribution
│   ├── create_kpf_targets.py     # Filter KPF targets from full dataset
│   └── download_ariel_data.py    # Download target data from Google Sheets
├── obs/                          # Observing blocks
│   ├── ob-template.json          # OB template with annotations
│   ├── obs_november_2025.json    # Full November OB list (32 targets)
│   └── obs_november_2025_test.json  # Test file (first 2 targets)
├── targets/                      # Target data files
│   ├── ariel_kpf_targets_20251016_162105.csv  # KPF targets only (131 targets)
│   └── ariel_targets_20251016_161910.csv      # Full target dataset (377 targets)
├── plots/                        # Generated plots (gitignored)
│   ├── november_airmass_all.png
│   └── november_targets_context.png
├── astroq_analysis/              # AstroQ analysis outputs (gitignored)
├── environment.yml               # Conda environment specification
├── requirements.txt              # Python package dependencies
├── project-description.txt       # Project requirements and guidelines
└── README.md                     # This file
```

## Setup Instructions

### 1. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate ariel-rv
```


## Usage

### Download Latest Target Data

```bash
cd bin
python download_ariel_data.py
```

Downloads fresh target data from Google Sheets (requires `credentials.json`).

### Filter KPF Targets

```bash
cd bin
python create_kpf_targets.py
```

### Generate November 2025 Observing Blocks

```bash
cd bin
python generate_obs_november.py
```

This will:
- Filter targets with RA = 20-24 hr (300-360 degrees) → 32 targets
- Generate OBs with observation window: November 1 - December 1, 2025
- Create two output files:
  - `../obs/obs_november_2025.json` - All 32 targets
  - `../obs/obs_november_2025_test.json` - First 2 targets (for testing upload)

### Plot November Target Distribution

```bash
cd bin
python plot_november_targets.py
```

Generates `../plots/november_targets_context.png` showing:
- November targets (RA 20-24hr) highlighted in context
- All KPF targets for reference
- Color-coded by V-magnitude

### Plot Airmass for November Targets

```bash
cd bin
python plot_november_airmass.py
```

Generates `../plots/november_airmass_all.png` showing:
- Airmass curves for all 32 November targets
- Centered on midnight Hawaii local time
- Annotated with target names
- Day/night shading using `astroplan`


Creates a CSV file with only KPF targets filtered from the full dataset.
