#!/usr/bin/env python3
"""
ARIEL-KPF Scheduling Tool - Night Allocation Module
Reads night allocation data from downloaded Keck CSV file.
"""

import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
import numpy as np


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
        
        return df
        
    except Exception as e:
        print(f"✗ Error reading CSV file: {e}")
        return None


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
    
    print("\n" + "="*60)


def create_night_allocation_plot(df, save_path='plots/kpf_night_allocation.png'):
    """
    Create a plot showing KPF-CC night allocation over time with dates on x-axis and UT time on y-axis.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        Night allocation DataFrame
    save_path : str
        Path to save the plot
    """
    if df is None or df.empty:
        print("No data to plot.")
        return
    
    # Filter for KPF-CC nights
    kpf_nights = df[df['Instrument'] == 'KPF-CC']
    
    if len(kpf_nights) == 0:
        print("No KPF-CC nights found to plot.")
        return
    
    # Convert Date column to datetime
    kpf_nights = kpf_nights.copy()
    kpf_nights['Date'] = pd.to_datetime(kpf_nights['Date'])
    
    # Parse time strings to extract start and end times
    def parse_time_string(time_str):
        """Parse time string like '10:28 - 15:07 ( 50%)' to extract start and end times."""
        try:
            # Extract the time part before the parentheses
            time_part = time_str.split(' (')[0]
            start_time, end_time = time_part.split(' - ')
            
            # Convert to datetime objects (using today's date as base)
            start_dt = pd.to_datetime(f"2025-01-01 {start_time}")
            end_dt = pd.to_datetime(f"2025-01-01 {end_time}")
            
            # Handle cases where end time is next day (e.g., 23:30 - 05:30)
            if end_dt < start_dt:
                end_dt += pd.Timedelta(days=1)
            
            return start_dt.time(), end_dt.time()
        except:
            return None, None
    
    # Parse all time strings
    start_times = []
    end_times = []
    for _, night in kpf_nights.iterrows():
        start_time, end_time = parse_time_string(night['Time'])
        start_times.append(start_time)
        end_times.append(end_time)
    
    kpf_nights['start_time'] = start_times
    kpf_nights['end_time'] = end_times
    
    # Sort by date and start time
    kpf_nights = kpf_nights.sort_values(['Date', 'start_time'])
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Plot each night as a horizontal bar
    for i, (_, night) in enumerate(kpf_nights.iterrows()):
        if night['start_time'] is None or night['end_time'] is None:
            continue
        
        # Calculate bar width (duration of observation)
        start_hour = night['start_time'].hour + night['start_time'].minute/60.0
        end_hour = night['end_time'].hour + night['end_time'].minute/60.0
        
        # Handle overnight observations
        if end_hour < start_hour:
            end_hour += 24
        
        bar_width = end_hour - start_hour
        
        # Create rectangle for each night
        rect = Rectangle((night['Date'], start_hour), 
                        pd.Timedelta(days=1), bar_width,
                        facecolor='blue', alpha=0.7, edgecolor='black', linewidth=0.5)
        ax.add_patch(rect)
    
    # Customize the plot
    ax.set_xlim(kpf_nights['Date'].min() - pd.Timedelta(days=5), 
                kpf_nights['Date'].max() + pd.Timedelta(days=5))
    
    # Set y-axis limits based on time range
    all_start_hours = [t.hour + t.minute/60.0 for t in start_times if t is not None]
    all_end_hours = [t.hour + t.minute/60.0 for t in end_times if t is not None]
    
    # Handle overnight observations
    adjusted_end_hours = []
    for i, end_hour in enumerate(all_end_hours):
        if i < len(all_start_hours) and end_hour < all_start_hours[i]:
            adjusted_end_hours.append(end_hour + 24)
        else:
            adjusted_end_hours.append(end_hour)
    
    min_hour = min(all_start_hours + adjusted_end_hours)
    max_hour = max(all_start_hours + adjusted_end_hours)
    
    ax.set_ylim(min_hour - 1, max_hour + 1)
    
    # Format x-axis as dates
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator())
    
    # Format y-axis as time
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"{int(x):02d}:{int((x-int(x))*60):02d}"))
    ax.yaxis.set_major_locator(plt.MultipleLocator(2))  # Every 2 hours
    ax.yaxis.set_minor_locator(plt.MultipleLocator(1))  # Every hour
    
    # Rotate x-axis labels
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Set labels and title
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('UT Time', fontsize=12, fontweight='bold')
    ax.set_title('KPF-CC Night Allocation Schedule\n(2025B Semester)', 
                fontsize=14, fontweight='bold')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Create plots directory if it doesn't exist
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Save the plot
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Night allocation plot saved to: {save_path}")
    
    plt.close()  # Close figure to free memory


def main():
    """
    Main function to read and analyze Keck night allocation data.
    """
    print("ARIEL-KPF Scheduling Tool - Night Allocation Analysis")
    print("=" * 60)
    
    # Read night allocation data
    df = read_keck_night_allocation()
    
    if df is not None:
        # Analyze KPF nights
        analyze_kpf_nights(df)
        
        # Create night allocation plot
        print("\n" + "="*60)
        print("CREATING NIGHT ALLOCATION PLOT")
        print("="*60)
        create_night_allocation_plot(df)
    else:
        print("\n✗ Failed to load night allocation data")
        print("Please ensure 'kpfcc-2025B.csv' is in the project directory")


if __name__ == "__main__":
    main()