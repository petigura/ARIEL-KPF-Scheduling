#!/usr/bin/env python3
"""
ARIEL-KPF Scheduling Tool - Night Allocation Module
Reads night allocation data from downloaded Keck CSV file.
"""

import pandas as pd
from datetime import datetime
import os


def read_keck_night_allocation(csv_file='kpfcc-2025B.csv'):
    """
    Read night allocation data from the downloaded Keck CSV file.
    
    Parameters:
    -----------
    csv_file : str
        Path to the Keck CSV file
        
    Returns:
    --------
    pandas.DataFrame
        DataFrame containing night allocation data
    """
    
    print(f"Reading Keck night allocation from: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"✗ File not found: {csv_file}")
        print("Please download the CSV file from:")
        print("https://www2.keck.hawaii.edu/observing/keckSchedule/queryForm.php")
        print("and save it as 'kpfcc-2025B.csv'")
        return None
    
    try:
        # Read the CSV file
        df = pd.read_csv(csv_file)
        
        print(f"✓ Successfully loaded {len(df)} nights")
        print(f"✓ Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"✗ Error reading CSV file: {e}")
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
    summary_lines.append("")
    
    # Add statistics
    if 'Date' in df.columns:
        summary_lines.append("Date range:")
        summary_lines.append(f"  Start: {df['Date'].min()}")
        summary_lines.append(f"  End: {df['Date'].max()}")
        summary_lines.append("")
    
    if 'Instrument' in df.columns:
        instrument_counts = df['Instrument'].value_counts()
        summary_lines.append("Instrument allocation:")
        for instrument, count in instrument_counts.items():
            summary_lines.append(f"  {instrument}: {count} nights")
        summary_lines.append("")
    
    if 'Account' in df.columns:
        account_counts = df['Account'].value_counts()
        summary_lines.append("Account allocation:")
        for account, count in account_counts.items():
            summary_lines.append(f"  {account}: {count} nights")
        summary_lines.append("")
    
    # Save summary
    with open(output_file, 'w') as f:
        f.write('\n'.join(summary_lines))
    
    print(f"✓ Summary saved to: {output_file}")


def analyze_kpf_nights(df):
    """
    Analyze KPF-CC specific nights for ARIEL targets.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Night allocation DataFrame
    """
    if df is None or df.empty:
        print("No data to analyze.")
        return
    
    print("\n" + "="*60)
    print("KPF-CC NIGHT ANALYSIS")
    print("="*60)
    
    # Filter for KPF-CC nights
    kpf_nights = df[df['Instrument'] == 'KPF-CC']
    
    print(f"Total KPF-CC nights: {len(kpf_nights)}")
    
    if len(kpf_nights) > 0:
        print(f"Date range: {kpf_nights['Date'].min()} to {kpf_nights['Date'].max()}")
        
        # Show available nights
        print("\nAvailable KPF-CC nights:")
        print("-" * 40)
        for _, night in kpf_nights.iterrows():
            print(f"{night['Date']}: {night['Time']} (Dark: {night['Dark']}%)")
        
        # Account analysis
        if 'Account' in kpf_nights.columns:
            print(f"\nAccount distribution:")
            account_counts = kpf_nights['Account'].value_counts()
            for account, count in account_counts.items():
                print(f"  {account}: {count} nights")
    
    print("\n" + "="*60)


def main():
    """
    Main function to read and analyze Keck night allocation data.
    """
    print("ARIEL-KPF Scheduling Tool - Night Allocation Analysis")
    print("=" * 60)
    
    # Read night allocation data
    df = read_keck_night_allocation()
    
    if df is not None:
        # Create summary
        create_night_allocation_summary(df)
        
        # Analyze KPF nights
        analyze_kpf_nights(df)
        
        # Display basic info
        print(f"\nNight allocation data loaded:")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        
        if not df.empty and 'Date' in df.columns:
            print(f"  Date range: {df['Date'].min()} to {df['Date'].max()}")
    else:
        print("\n✗ Failed to load night allocation data")
        print("Please ensure 'kpfcc-2025B.csv' is in the project directory")


if __name__ == "__main__":
    main()