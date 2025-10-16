# ARIEL-KPF Scheduling Tool

A Python-based repository for scheduling targets on the Keck telescope. This tool connects to a Google Spreadsheet containing target information and helps prepare observing blocks (OBs) for submission to Keck Observatory.

## Software Components

### Core Dependencies
- **astropy**: For coordinate transformations and astronomical calculations
- **pandas**: For data manipulation and analysis of target information
- **matplotlib**: For visualization of target data and scheduling plots
- **google-api-python-client**: For connecting to Google Sheets API
- **gspread**: Python API for Google Sheets

### Project Structure
```
ARIEL-KPF-Scheduling/
├── main.py                 # Main script for step 1 - Google Sheets connection
├── environment.yml         # Conda environment specification
├── requirements.txt        # Python package dependencies (legacy)
├── README.md              # This file
├── .gitignore             # Git ignore patterns
└── credentials.json       # Google service account credentials (not tracked)
```

## Setup Instructions

### 1. Create Conda Environment
```bash
conda env create -f environment.yml
conda activate ariel-kpf-scheduling
```

### 2. Google Sheets API Setup
To connect to the Google Spreadsheet, you need to set up Google Sheets API access:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Sheets API
4. Create a service account and download the credentials JSON file
5. Save the credentials file as `credentials.json` in the project directory
6. Share the Google Spreadsheet with the service account email address

### 3. Run the Application
```bash
python main.py
```

## Current Features (Step 1)

The current implementation focuses on Step 1 of the project:

- **Google Sheets Connection**: Connects to the target spreadsheet using Google Sheets API
- **Target Data Display**: Reads and displays target information including:
  - Right Ascension (RA)
  - Declination (DEC) 
  - V-magnitude
- **Data Analysis**: Automatically detects relevant columns and provides data overview

## Target Spreadsheet

The targets are stored in this Google Spreadsheet:
https://docs.google.com/spreadsheets/d/1gAAznK9h4rC-JTsTA1V8eBtJKIj53AjrTiyIJVjrGuE/edit?gid=1500126039#gid=1500126039

## Observing Blocks (OBs)

The targets will be scheduled by submitting observing blocks (OBs) to Keck Observatory. These OBs are batch submitted as JSON files with specific fields and formatting requirements. This tool will eventually generate properly formatted JSON files for batch submission to Keck.

## Future Development

This is the foundation for a more comprehensive scheduling tool that will:
- Process target coordinates and magnitudes
- Generate observing blocks (OBs) for Keck Observatory in JSON format
- Batch submit OBs to Keck Observatory
- Provide scheduling recommendations based on target visibility
- Create visualizations for observing planning

## Contributing

This project is designed for ARIEL-KPF telescope scheduling. Please ensure any modifications maintain compatibility with Keck Observatory's observing block format requirements.
