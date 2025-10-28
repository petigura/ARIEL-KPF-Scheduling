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
├── plots/                        # Generated plots (gitignored)
│   ├── november_airmass_all.png
│   └── november_targets_context.png
├── astroq_analysis/              # AstroQ analysis outputs (gitignored)
├── ariel_kpf_targets_*.csv       # Target data files
├── ariel_targets_*.csv           # Full target dataset
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

### 2. Install Additional Dependencies (if needed)
```bash
pip install astroplan  # For airmass plotting
```

### 3. Google Sheets API Setup (Optional)

For downloading fresh target data from Google Sheets:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a service account and download the credentials JSON file
5. Save the credentials file as `credentials.json` in the project directory
6. Share the Google Spreadsheet with the service account email address

**Target Spreadsheet URL**: https://docs.google.com/spreadsheets/d/1gAAznK9h4rC-JTsTA1V8eBtJKIj53AjrTiyIJVjrGuE/edit?usp=sharing

## Usage

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

Creates a CSV file with only KPF targets filtered from the full dataset.

## Observing Block Format

Observing blocks are JSON files that follow the Keck OB format specification. Each OB contains:

1. **Target section**: Coordinates, identifiers, proper motion
2. **Calibration section**: Calibration lamp settings
3. **Observation section**: Exposure settings, filters, guiding
4. **Schedule section**: Time constraints, cadence, elevation limits
5. **Metadata section**: Additional information (kept as empty dict)

**Key Features:**
- Time constraints set to observing window (Nov 1 - Dec 1, 2025)
- Fields like `total_observations_requested` are removed (auto-filled by KPF-CC webpage)
- `TargetName` and `Object` fields match (e.g., "TIC117689799")
- Proper handling of JSON comments in template

**Keck OB Building Guide**: https://www2.keck.hawaii.edu/inst/kpf/buildingOBs/

## November 2025 Targets

The November observing window targets 32 ARIEL planets with:
- **RA Range**: 300.74° to 356.48° (20:03hr to 23:46hr)
- **Observing Window**: November 1 - December 1, 2025
- **Scheduling**: 4 visits per target within the month
- **Cadence**: Minimum 1 night between visits

These targets were selected for optimal visibility during November nights at Keck Observatory (Mauna Kea, Hawaii).

## Core Dependencies

- **astropy**: Coordinate transformations, time handling, astronomical calculations
- **astroplan**: Observation planning, airmass calculations, visibility windows
- **pandas**: Data manipulation and filtering
- **matplotlib**: Plotting and visualization
- **numpy**: Numerical computations
- **google-api-python-client**: Google Sheets API access
- **gspread**: Python API for Google Sheets

## Observing Strategy

The observing strategy is to obtain **four RVs (radial velocity measurements) of each ARIEL target within a month-long observing window**. This approach:

- Provides sufficient phase coverage for planetary characterization
- Allows for weather and scheduling flexibility
- Enables detection of systematic effects
- Supports the ARIEL mission's atmospheric characterization goals

Targets are grouped by RA into monthly observing windows to ensure optimal visibility and efficient telescope scheduling.

## Keck Observatory Resources

- **KPF Instrument**: https://www2.keck.hawaii.edu/inst/kpf/
- **Building OBs Guide**: https://www2.keck.hawaii.edu/inst/kpf/buildingOBs/
- **Keck Schedule**: https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php
- **Program N427**: Manual OB upload to Keck Observatory system

## File Formats

### Input Files
- **CSV**: Target lists with RA, Dec, magnitudes, planet properties
- **JSON**: OB template with annotations for guidance

### Output Files
- **JSON**: Observing blocks ready for upload to Keck
- **PNG**: Plots for observation planning and target visualization

## Development Notes

### Recent Changes
- Reorganized repository: scripts → `bin/`, OBs → `obs/`
- Removed vestigial plotting code
- Added `.gitignore` for `plots/` and `astroq_analysis/`
- Generated November 2025 OBs (32 targets)
- Created airmass and sky distribution plots

### Code Quality
- Scripts use relative paths for portability
- JSON comment stripping for template parsing
- Proper coordinate conversion (degrees ↔ sexagesimal)
- Git history preserved through `git mv` operations

## Contributing

This project is designed for ARIEL-KPF telescope scheduling. Key considerations:

- Maintain compatibility with Keck Observatory's OB format
- Follow the template structure in `obs/ob-template.json`
- Test OB generation with small sample before full run
- Verify coordinates and time constraints before submission
- Keep `ob-template.json` annotations for future reference

## Contact

For questions about ARIEL targets, observing strategy, or Keck scheduling, please refer to the project team.

## License

This project is for scientific research purposes as part of the ARIEL mission preparation.
