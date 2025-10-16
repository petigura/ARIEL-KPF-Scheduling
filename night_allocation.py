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


def download_keck_night_allocation(instrument='KPF-CC', semester='2025B', output_file='keck_night_allocation.csv'):
    """
    Download night allocation data from Keck Observatory website.
    
    Parameters:
    -----------
    instrument : str
        Instrument name (default: 'KPF-CC')
    semester : str
        Semester (default: '2025B')
    output_file : str
        Output CSV filename
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing night allocation data
    """
    
    print(f"Downloading Keck night allocation for {instrument} - {semester}...")
    
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
            print("Found form, attempting to submit...")
            return submit_keck_form(form, instrument, semester, output_file)
        else:
            print("No form found, trying direct CSV approach...")
            return try_direct_csv_download(instrument, semester, output_file)
            
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


def try_direct_csv_download(instrument, semester, output_file):
    """Try direct CSV download with various parameter combinations."""
    
    base_url = "https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php"
    
    # Try different parameter combinations
    param_combinations = [
        {'instrument': instrument, 'semester': semester, 'format': 'csv'},
        {'inst': instrument, 'sem': semester, 'output': 'csv'},
        {'instrument': instrument, 'semester': semester},
        {'inst': instrument, 'sem': semester}
    ]
    
    for params in param_combinations:
        try:
            print(f"Trying parameters: {params}")
            response = requests.get(base_url, params=params, timeout=30)
            
            if response.text.startswith('Date,') or 'csv' in response.headers.get('content-type', ''):
                # Save CSV data
                with open(output_file, 'w') as f:
                    f.write(response.text)
                
                df = pd.read_csv(output_file)
                print(f"✓ Successfully downloaded {len(df)} nights")
                print(f"✓ Data saved to: {output_file}")
                return df
                
        except Exception as e:
            print(f"Failed with params {params}: {e}")
            continue
    
    print("Direct CSV download failed. Manual download required.")
    return None


def submit_keck_form(form, instrument, semester, output_file):
    """Submit the Keck form with proper parameters."""
    
    # Extract form action URL
    action = form.get('action', '')
    if not action.startswith('http'):
        action = "https://www2.keck.hawaii.edu/observing/keckSchedule/" + action
    
    # Find all input fields
    inputs = form.find_all('input')
    form_data = {}
    
    for input_field in inputs:
        name = input_field.get('name')
        value = input_field.get('value', '')
        if name:
            form_data[name] = value
    
    # Set our desired parameters
    form_data['instrument'] = instrument
    form_data['semester'] = semester
    form_data['format'] = 'csv'
    
    try:
        print(f"Submitting form to: {action}")
        response = requests.post(action, data=form_data, timeout=30)
        
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
            '2025-08-06', '2025-08-07', '2025-08-08', '2025-08-09', '2025-08-10'
        ],
        'Instrument': ['KPF-CC'] * 10,
        'Semester': ['2025B'] * 10,
        'Allocated': ['Yes'] * 10,
        'Notes': ['Sample data - replace with actual Keck schedule'] * 10
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('keck_night_allocation_sample.csv', index=False)
    
    print("✓ Sample template created: keck_night_allocation_sample.csv")
    print("📝 Please replace this with actual data from:")
    print("   https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php")
    print("   Select: Instrument=KPF-CC, Semester=2025B")
    
    return df


if __name__ == "__main__":
    main()
