#!/usr/bin/env python3
"""
ARIEL-KPF Scheduling Tool - Night Allocation Module
Downloads night allocation data from Keck Observatory website.
"""

import pandas as pd
import requests
from datetime import datetime
import os
from bs4 import BeautifulSoup
import time


def download_keck_night_allocation(instrument='KPF-CC', semester='2025B', 
                                   start_date='2025-08-01', end_date='2025-12-31',
                                   output_file='keck_night_allocation.csv'):
    """
    Download night allocation data from Keck Observatory website.
    
    Parameters:
    -----------
    instrument : str
        Instrument name (default: 'KPF-CC')
    semester : str
        Semester (default: '2025B')
    start_date : str
        Start date in YYYY-MM-DD format (default: '2025-08-01')
    end_date : str
        End date in YYYY-MM-DD format (default: '2025-12-31')
    output_file : str
        Output CSV filename
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing night allocation data
    """
    
    print(f"Downloading Keck night allocation for {instrument} - {semester}...")
    print(f"Date range: {start_date} to {end_date}")
    
    # Keck schedule query URL
    base_url = "https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php"
    
    try:
        # First, get the form page to understand the structure
        print("Fetching Keck schedule form...")
        response = requests.get(base_url, timeout=30)
        response.raise_for_status()
        
        # Parse the HTML form
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for form elements
        form = soup.find('form')
        if form:
            print("Found form, attempting to submit with proper parameters...")
            return submit_keck_form_with_dates(form, instrument, semester, start_date, end_date, output_file)
        else:
            print("No form found, trying direct CSV approach...")
            return try_direct_csv_download_with_dates(instrument, semester, start_date, end_date, output_file)
            
    except requests.exceptions.RequestException as e:
        print(f"Error accessing Keck website: {e}")
        print("This might be due to:")
        print("1. Website requiring authentication")
        print("2. Network connectivity issues")
        print("3. Website structure changes")
        return None
    except Exception as e:
        print(f"Error processing Keck data: {e}")
        return None


def try_direct_csv_download_with_dates(instrument, semester, start_date, end_date, output_file):
    """Try direct CSV download with date parameters."""
    
    base_url = "https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php"
    
    # Try different parameter combinations with dates
    param_combinations = [
        {
            'doQuery': '1',
            'table': 'schedule',
            'Instrument': instrument,
            'sem': semester,
            'Date': f"{start_date} to {end_date}",
            'excel': 'on',
            'cb_Instrument': 'on',
            'cb_Date': 'on',
            'sched': 'Query Tel Schedule'
        },
        {
            'Instrument': instrument,
            'semester': semester,
            'start_date': start_date,
            'end_date': end_date,
            'format': 'csv'
        },
        {
            'inst': instrument,
            'sem': semester,
            'start': start_date,
            'end': end_date,
            'output': 'csv'
        },
        {
            'instrument': instrument,
            'semester': semester,
            'start_date': start_date,
            'end_date': end_date
        }
    ]
    
    for params in param_combinations:
        try:
            print(f"Trying parameters: {params}")
            response = requests.get(base_url, params=params, timeout=30)
            
            print(f"Response status: {response.status_code}")
            print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
            print(f"Response preview: {response.text[:200]}...")
            
            if response.text.startswith('Date,') or 'csv' in response.headers.get('content-type', ''):
                # Save CSV data
                with open(output_file, 'w') as f:
                    f.write(response.text)
                
                df = pd.read_csv(output_file)
                print(f"✓ Successfully downloaded {len(df)} nights")
                print(f"✓ Data saved to: {output_file}")
                return df
            elif 'csv' in response.text.lower() or 'schedule' in response.text.lower():
                # Might be CSV data with different headers
                print("Response appears to contain schedule data, attempting to parse...")
                with open(output_file, 'w') as f:
                    f.write(response.text)
                
                try:
                    df = pd.read_csv(output_file)
                    print(f"✓ Successfully parsed {len(df)} nights")
                    print(f"✓ Data saved to: {output_file}")
                    return df
                except Exception as e:
                    print(f"Failed to parse as CSV: {e}")
                    continue
                
        except Exception as e:
            print(f"Failed with params {params}: {e}")
            continue
    
    print("Direct CSV download failed. Manual download required.")
    return None


def analyze_keck_form():
    """Analyze the Keck form structure to understand the correct field names."""
    
    print("Analyzing Keck form structure...")
    
    try:
        response = requests.get("https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php", timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all forms
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms")
        
        for i, form in enumerate(forms):
            print(f"\nForm {i+1}:")
            print(f"  Action: {form.get('action', 'N/A')}")
            print(f"  Method: {form.get('method', 'N/A')}")
            
            # Find all input fields
            inputs = form.find_all('input')
            print(f"  Input fields ({len(inputs)}):")
            for inp in inputs:
                name = inp.get('name', 'N/A')
                input_type = inp.get('type', 'text')
                value = inp.get('value', '')
                print(f"    {name} ({input_type}): {value}")
            
            # Find all select fields
            selects = form.find_all('select')
            print(f"  Select fields ({len(selects)}):")
            for sel in selects:
                name = sel.get('name', 'N/A')
                options = sel.find_all('option')
                print(f"    {name}:")
                for opt in options:
                    opt_value = opt.get('value', '')
                    opt_text = opt.get_text().strip()
                    selected = opt.get('selected', False)
                    print(f"      {opt_value}: {opt_text} {'(selected)' if selected else ''}")
        
        return True
        
    except Exception as e:
        print(f"Error analyzing form: {e}")
        return False


def submit_keck_form_with_dates(form, instrument, semester, start_date, end_date, output_file):
    """Submit the Keck form with proper parameters including dates."""
    
    # Extract form action URL
    action = form.get('action', '')
    if not action.startswith('http'):
        action = "https://www2.keck.hawaii.edu/observing/keckSchedule/" + action
    
    # Find all input fields
    inputs = form.find_all('input')
    selects = form.find_all('select')
    form_data = {}
    
    # Process input fields
    for input_field in inputs:
        name = input_field.get('name')
        value = input_field.get('value', '')
        input_type = input_field.get('type', 'text')
        
        if name:
            if input_type == 'checkbox' or input_type == 'radio':
                if input_field.get('checked'):
                    form_data[name] = value
            else:
                form_data[name] = value
    
    # Process select fields
    for select_field in selects:
        name = select_field.get('name')
        if name:
            selected_option = select_field.find('option', selected=True)
            if selected_option:
                form_data[name] = selected_option.get('value', '')
            else:
                # Use first option as default
                first_option = select_field.find('option')
                if first_option:
                    form_data[name] = first_option.get('value', '')
    
    # Set our desired parameters based on actual form structure
    form_data['Instrument'] = instrument  # Text field for instrument
    form_data['sem'] = semester  # Select field for semester
    form_data['Date'] = f"{start_date} to {end_date}"  # Date range in text field
    form_data['excel'] = 'on'  # Checkbox for CSV format
    form_data['cb_Instrument'] = 'on'  # Checkbox to enable instrument filter
    form_data['cb_Date'] = 'on'  # Checkbox to enable date filter
    
    # Debug: print form data
    print(f"Form data being submitted: {form_data}")
    
    try:
        print(f"Submitting form to: {action}")
        response = requests.post(action, data=form_data, timeout=30)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content preview: {response.text[:500]}...")
        
        if response.text.startswith('Date,') or 'csv' in response.headers.get('content-type', ''):
            # Save CSV data
            with open(output_file, 'w') as f:
                f.write(response.text)
            
            df = pd.read_csv(output_file)
            print(f"✓ Successfully downloaded {len(df)} nights")
            print(f"✓ Data saved to: {output_file}")
            return df
        else:
            print("Form submission did not return CSV data")
            print("Response content type:", response.headers.get('content-type', 'unknown'))
            return None
            
    except Exception as e:
        print(f"Error submitting form: {e}")
        return None




def create_night_allocation_summary(df, output_file='night_allocation_summary.txt'):
    """
    Create a summary of the night allocation data.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Night allocation DataFrame
    output_file : str
        Output summary filename
    """
    if df is None or df.empty:
        print("No night allocation data to summarize.")
        return
    
    print(f"\nCreating night allocation summary...")
    
    summary_lines = []
    summary_lines.append("KECK NIGHT ALLOCATION SUMMARY")
    summary_lines.append("=" * 50)
    summary_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append(f"Total nights: {len(df)}")
    summary_lines.append("")
    
    # Add column information
    summary_lines.append("Available columns:")
    for i, col in enumerate(df.columns, 1):
        summary_lines.append(f"  {i:2d}. {col}")
    summary_lines.append("")
    
    # Add sample data
    summary_lines.append("Sample data (first 5 rows):")
    summary_lines.append("-" * 50)
    summary_lines.append(df.head().to_string(index=False))
    
    # Save summary
    with open(output_file, 'w') as f:
        f.write('\n'.join(summary_lines))
    
    print(f"✓ Summary saved to: {output_file}")


def main():
    """
    Main function to download and process Keck night allocation data.
    """
    print("ARIEL-KPF Scheduling Tool - Night Allocation Download")
    print("=" * 60)
    
    # Download night allocation data
    df = download_keck_night_allocation()
    
    if df is not None:
        # Create summary
        create_night_allocation_summary(df)
        
        # Display basic info
        print(f"\nNight allocation data loaded:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        
        if not df.empty:
            print(f"  Date range: {df.iloc[0, 0]} to {df.iloc[-1, 0]}")
    else:
        print("\n✗ Failed to download night allocation data")
        print("Creating sample template instead...")
        
        # Create sample data as fallback
        df = create_sample_night_allocation()
        create_night_allocation_summary(df, 'night_allocation_sample_summary.txt')


def create_manual_download_instructions():
    """Create detailed instructions for manual download."""
    
    instructions = """
KECK NIGHT ALLOCATION - MANUAL DOWNLOAD INSTRUCTIONS
==================================================

The Keck website requires manual interaction to download the CSV file.
Please follow these steps:

1. Open your web browser and go to:
   https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php

2. Fill out the form with these exact values:
   - Semester: 2025B
   - Instrument: KPF-CC
   - Start Date: 2025-08-01
   - End Date: 2025-12-31
   - Format: CSV (check the Excel checkbox)

3. Click "Query Tel Schedule" button

4. The website should generate a CSV file that downloads automatically

5. Save the downloaded file as: keck_night_allocation.csv

6. Place the file in the project directory

7. Run the analysis again:
   python night_allocation.py

ALTERNATIVE: Use the sample template
====================================
If you cannot access the Keck website, use the sample template:
keck_night_allocation_sample.csv

This contains the expected structure and can be modified with actual dates.
"""
    
    with open('keck_download_instructions.txt', 'w') as f:
        f.write(instructions)
    
    print("📝 Manual download instructions saved to: keck_download_instructions.txt")
    print(instructions)


def create_sample_night_allocation():
    """
    Create a sample night allocation CSV file with the expected structure.
    This serves as a template until the actual data can be downloaded.
    """
    
    print("Creating sample night allocation template...")
    
    # Sample data structure based on typical Keck schedule format
    sample_data = {
        'Date': [
            '2025-08-01', '2025-08-02', '2025-08-03', '2025-08-04', '2025-08-05',
            '2025-08-06', '2025-08-07', '2025-08-08', '2025-08-09', '2025-08-10',
            '2025-08-11', '2025-08-12', '2025-08-13', '2025-08-14', '2025-08-15',
            '2025-08-16', '2025-08-17', '2025-08-18', '2025-08-19', '2025-08-20'
        ],
        'Instrument': ['KPF-CC'] * 20,
        'Semester': ['2025B'] * 20,
        'Allocated': ['Yes'] * 20,
        'Notes': ['Sample data - replace with actual Keck schedule'] * 20
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('keck_night_allocation_sample.csv', index=False)
    
    print("✓ Sample template created: keck_night_allocation_sample.csv")
    print("📝 Please replace this with actual data from:")
    print("   https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php")
    print("   Select: Instrument=KPF-CC, Semester=2025B")
    print("   Date range: 2025-08-01 to 2025-12-31")
    print("   Format: CSV")
    
    # Create manual download instructions
    create_manual_download_instructions()
    
    return df


if __name__ == "__main__":
    main()
