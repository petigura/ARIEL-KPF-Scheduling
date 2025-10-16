#!/usr/bin/env python3
"""
ARIEL-KPF Scheduling Tool
Main script for connecting to Google Sheets and displaying target information.
"""

import pandas as pd
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
from astropy import units as u
import gspread
from google.oauth2.service_account import Credentials
import os
from visualization import create_all_plots


def connect_to_google_sheets():
    """
    Connect to Google Sheets using service account credentials.
    Returns a gspread client object.
    """
    # Define the scope for Google Sheets access
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Check if credentials file exists
    creds_file = "credentials.json"
    if not os.path.exists(creds_file):
        print(f"Error: {creds_file} not found!")
        print("Please download your service account credentials from Google Cloud Console")
        print("and save them as 'credentials.json' in the project directory.")
        return None
    
    try:
        # Load credentials
        creds = Credentials.from_service_account_file(creds_file, scopes=scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"Error connecting to Google Sheets: {e}")
        return None


def read_target_data_public(spreadsheet_url):
    """
    Read target data from a publicly accessible Google Spreadsheet.
    This method doesn't require authentication but may have limitations.
    
    Parameters:
    -----------
    spreadsheet_url : str
        Public URL of the Google Spreadsheet
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing target information
    """
    try:
        # Extract spreadsheet ID from URL
        if 'spreadsheets/d/' in spreadsheet_url:
            spreadsheet_id = spreadsheet_url.split('spreadsheets/d/')[1].split('/')[0]
        else:
            raise ValueError("Invalid Google Spreadsheet URL format")
        
        # Try different CSV export URLs
        csv_urls = [
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=0",
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv",
            f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=1500126039"
        ]
        
        for csv_url in csv_urls:
            try:
                print(f"Trying CSV URL: {csv_url}")
                df = pd.read_csv(csv_url)
                if not df.empty:
                    print(f"✓ Successfully read data from: {csv_url}")
                    return df
            except Exception as e:
                print(f"Failed with URL {csv_url}: {e}")
                continue
        
        # If all CSV URLs fail, try using requests with headers
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        for csv_url in csv_urls:
            try:
                print(f"Trying with requests: {csv_url}")
                response = requests.get(csv_url, headers=headers)
                if response.status_code == 200:
                    from io import StringIO
                    df = pd.read_csv(StringIO(response.text))
                    if not df.empty:
                        print(f"✓ Successfully read data with requests from: {csv_url}")
                        return df
            except Exception as e:
                print(f"Failed with requests for URL {csv_url}: {e}")
                continue
        
        raise Exception("All public access methods failed")
        
    except Exception as e:
        print(f"Error reading public spreadsheet data: {e}")
        return None


def read_target_data_authenticated(client, spreadsheet_url):
    """
    Read target data from the Google Spreadsheet.
    
    Parameters:
    -----------
    client : gspread.Client
        Authenticated Google Sheets client
    spreadsheet_url : str
        URL of the Google Spreadsheet
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing target information
    """
    try:
        # Open the spreadsheet
        spreadsheet = client.open_by_url(spreadsheet_url)
        
        # Get the first worksheet (or specify by name if needed)
        worksheet = spreadsheet.sheet1
        
        # Get all records as a list of dictionaries
        records = worksheet.get_all_records()
        
        # Convert to DataFrame
        df = pd.DataFrame(records)
        
        return df
        
    except Exception as e:
        print(f"Error reading spreadsheet data: {e}")
        return None


def display_target_info(df):
    """
    Display target RA, DEC, V-magnitude, period, and radius information.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    """
    if df is None or df.empty:
        print("No data available to display.")
        return
    
    print("\n" + "="*60)
    print("TARGET INFORMATION")
    print("="*60)
    
    # Display basic info about the dataset
    print(f"Total targets: {len(df)}")
    print(f"Columns available: {list(df.columns)}")
    print()
    
    # Try to identify RA, DEC, V-magnitude, period, and radius columns
    # Common column names for these fields
    ra_cols = [col for col in df.columns if any(keyword in col.lower() 
               for keyword in ['ra', 'right ascension', 'alpha'])]
    dec_cols = [col for col in df.columns if any(keyword in col.lower() 
                for keyword in ['dec', 'declination', 'delta'])]
    vmag_cols = [col for col in df.columns if any(keyword in col.lower() 
                 for keyword in ['vmag', 'v_mag', 'magnitude', 'mag'])]
    period_cols = [col for col in df.columns if any(keyword in col.lower() 
                   for keyword in ['period', 'p', 'orbital period'])]
    radius_cols = [col for col in df.columns if any(keyword in col.lower() 
                   for keyword in ['radius', 'r', 'r_planet', 'r_p', 'planetary radius'])]
    
    print("Detected columns:")
    print(f"  RA columns: {ra_cols}")
    print(f"  DEC columns: {dec_cols}")
    print(f"  V-magnitude columns: {vmag_cols}")
    print(f"  Period columns: {period_cols}")
    print(f"  Radius columns: {radius_cols}")
    print()
    
    # Display first few rows of relevant data
    relevant_cols = ra_cols + dec_cols + vmag_cols + period_cols + radius_cols
    if relevant_cols:
        print("Sample data (first 5 rows):")
        print("-" * 60)
        print(df[relevant_cols].head().to_string(index=False))
    else:
        print("Could not automatically identify RA, DEC, V-magnitude, period, or radius columns.")
        print("Available columns:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
    
    print("\n" + "="*60)


def main():
    """
    Main function to execute step 1 of the ARIEL-KPF scheduling tool.
    """
    print("ARIEL-KPF Scheduling Tool - Step 1")
    print("Connecting to Google Sheets and displaying target information...")
    
    # Google Spreadsheet URLs
    spreadsheet_url_public = "https://docs.google.com/spreadsheets/d/1gAAznK9h4rC-JTsTA1V8eBtJKIj53AjrTiyIJVjrGuE/edit?usp=sharing"
    spreadsheet_url_private = "https://docs.google.com/spreadsheets/d/1gAAznK9h4rC-JTsTA1V8eBtJKIj53AjrTiyIJVjrGuE/edit?gid=1500126039#gid=1500126039"
    
    print("\nAttempting to read spreadsheet data...")
    
    # Try public access first (no authentication required)
    print("Trying public access...")
    df = read_target_data_public(spreadsheet_url_public)
    
    if df is not None and not df.empty:
        print("✓ Successfully read data via public access")
        display_target_info(df)
        
        # Create visualization plots
        print("\n" + "="*60)
        print("CREATING VISUALIZATION PLOTS")
        print("="*60)
        create_all_plots(df)
        return
    
    # If public access fails, try authenticated access
    print("Public access failed, trying authenticated access...")
    client = connect_to_google_sheets()
    if client is None:
        print("✗ Could not establish authenticated connection")
        print("Please check your credentials.json file and Google Sheets API setup")
        return
    
    # Read target data using authenticated access
    df = read_target_data_authenticated(client, spreadsheet_url_private)
    if df is None:
        print("✗ Could not read data via authenticated access")
        return
    
    print("✓ Successfully read data via authenticated access")
    display_target_info(df)
    
    # Create visualization plots
    print("\n" + "="*60)
    print("CREATING VISUALIZATION PLOTS")
    print("="*60)
    create_all_plots(df)


if __name__ == "__main__":
    main()
