#!/usr/bin/env python3
"""
Download ARIEL targets data from Google Sheets and save as CSV
"""

import pandas as pd
import requests
from datetime import datetime

def download_ariel_targets_csv():
    """Download ARIEL targets data from Google Sheets and save as CSV."""
    
    print("Downloading ARIEL targets data from Google Sheets...")
    
    # Google Sheets public CSV URL
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1gAAznK9h4rC-JTsTA1V8eBtJKIj53AjrTiyIJVjrGuE/export?format=csv"
    
    try:
        # Download the data
        print(f"Fetching data from: {spreadsheet_url}")
        df = pd.read_csv(spreadsheet_url)
        
        print(f"✅ Successfully downloaded data!")
        print(f"📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Save as CSV
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"../targets/ariel_targets_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print(f"💾 Data saved to: {filename}")
        
        # Display sample data
        print("\n" + "="*80)
        print("SAMPLE DATA (first 5 rows)")
        print("="*80)
        print(df.head().to_string())
        
        print("\n" + "="*80)
        print("DATA SUMMARY")
        print("="*80)
        print(f"Total targets: {len(df)}")
        print(f"KPF targets: {df['observe_kpf'].sum() if 'observe_kpf' in df.columns else 'N/A'}")
        print(f"NEID targets: {df['observe_neid'].sum() if 'observe_neid' in df.columns else 'N/A'}")
        
        # Show coordinate ranges
        if 'ra' in df.columns and 'dec' in df.columns:
            print(f"\nCoordinate ranges:")
            print(f"  RA: {df['ra'].min():.3f}° to {df['ra'].max():.3f}°")
            print(f"  DEC: {df['dec'].min():.3f}° to {df['dec'].max():.3f}°")
        
        # Show magnitude ranges
        if 'v_mag' in df.columns:
            v_mag_data = df['v_mag'].dropna()
            if len(v_mag_data) > 0:
                print(f"  V magnitude: {v_mag_data.min():.2f} to {v_mag_data.max():.2f}")
        
        if 'tess_mag' in df.columns:
            tess_mag_data = df['tess_mag'].dropna()
            if len(tess_mag_data) > 0:
                print(f"  TESS magnitude: {tess_mag_data.min():.2f} to {tess_mag_data.max():.2f}")
        
        # Show planet properties
        if 'planet_radius' in df.columns:
            radius_data = df['planet_radius'].dropna()
            if len(radius_data) > 0:
                print(f"  Planet radius: {radius_data.min():.2f} to {radius_data.max():.2f} Earth radii")
        
        if 'period' in df.columns:
            period_data = df['period'].dropna()
            if len(period_data) > 0:
                print(f"  Planet period: {period_data.min():.3f} to {period_data.max():.3f} days")
        
        return df, filename
        
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return None, None

def main():
    print("ARIEL-KPF Google Sheets Data Download")
    print("=" * 50)
    
    df, filename = download_ariel_targets_csv()
    
    if df is not None:
        print(f"\n✅ Download complete!")
        print(f"📁 File saved as: {filename}")
        print(f"📊 Data contains {len(df)} targets with {len(df.columns)} columns")
    else:
        print("\n❌ Download failed!")

if __name__ == "__main__":
    main()
