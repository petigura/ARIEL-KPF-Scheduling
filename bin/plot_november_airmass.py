#!/usr/bin/env python3
"""
Plot airmass for November 2025 targets
Following the format from project-description.txt using astroplan
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroplan import FixedTarget, Observer
from astroplan.plots import plot_airmass
import numpy as np

# Disable IERS auto-update (working offline)
from astropy.utils import iers
iers.conf.auto_max_age = None


def plot_november_airmass():
    """
    Plot airmass for all November targets using astroplan.
    Following the format from project-description.txt:
    
    time = Time('2018-01-02 19:00')
    target = FixedTarget.from_name('HD 189733')
    keck = Observer.at_site('Keck')
    plot_airmass(target, keck, time, brightness_shading=True, altitude_yaxis=True)
    """
    print("="*80)
    print("Plotting Airmass for November 2025 Targets")
    print("="*80)
    
    # Load target data
    print("\n1. Loading target data...")
    csv_file = "../targets/ariel_kpf_targets_20251016_162105.csv"
    df = pd.read_csv(csv_file)
    
    # Filter for KPF targets only
    df_kpf = df[df['observe_kpf'] == True].copy()
    
    # Identify November targets (RA 300-360°)
    november_mask = (df_kpf['ra'] >= 300) & (df_kpf['ra'] <= 360)
    df_november = df_kpf[november_mask].copy()
    
    print(f"   Total November targets: {len(df_november)}")
    
    # Set up observer and time (following project-description.txt format)
    print("\n2. Setting up Keck Observatory and observation time...")
    keck = Observer.at_site('Keck')
    
    # Center plot on midnight Hawaii local time (HST = UTC-10)
    # Midnight HST = 10:00 UTC
    time = Time('2025-11-16 10:00')  # UTC time for midnight HST
    print(f"   Observation time (centered on): {time.iso} UTC (midnight HST)")
    print(f"   Observatory: Keck (Mauna Kea, Hawaii)")
    
    # Create figure
    print("\n3. Creating airmass plot for all November targets...")
    fig, ax = plt.subplots(figsize=(16, 8))
    
    # Sort by RA to keep consistent ordering
    df_november_sorted = df_november.sort_values('ra')
    
    # Plot all targets using astroplan's plot_airmass
    for idx, row in df_november_sorted.iterrows():
        ticid = int(row['ticid'])
        ra_deg = row['ra']
        dec_deg = row['dec']
        vmag = row['v_mag'] if pd.notna(row['v_mag']) else 0
        
        # Create FixedTarget using coordinates
        coord = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame='icrs')
        target = FixedTarget(coord=coord, name=f"TIC{ticid}")
        
        try:
            # Use astroplan's plot_airmass (following project-description.txt format)
            plot_airmass(target, keck, time, 
                        brightness_shading=True,
                        altitude_yaxis=True,
                        ax=ax,
                        style_kwargs={'alpha': 0.6, 'linewidth': 1.5})
            
            # Add annotation at the minimum airmass point
            # Get the airmass data from the line we just plotted
            line = ax.get_lines()[-1]
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            line_color = line.get_color()  # Get the color that was automatically assigned
            
            # Convert to plain numpy arrays if they are Quantity objects
            if hasattr(ydata, 'value'):
                ydata = ydata.value
            if hasattr(xdata, 'value'):
                xdata = xdata.value
            
            # Find minimum airmass
            valid_mask = ~np.isnan(ydata)
            if np.any(valid_mask):
                min_idx = np.nanargmin(ydata)
                if valid_mask[min_idx]:
                    ax.annotate(f'TIC{ticid}', 
                               xy=(xdata[min_idx], ydata[min_idx]),
                               xytext=(3, 0), textcoords='offset points',
                               fontsize=7, alpha=0.8, color=line_color,
                               bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                       edgecolor=line_color, alpha=0.7, linewidth=0.5))
        except Exception as e:
            print(f"   Warning: Could not plot TIC{ticid}: {e}")
    
    # Customize the plot
    ax.set_xlabel('Time (Hours)', fontsize=12)
    ax.set_ylabel('Airmass', fontsize=12)
    ax.set_title(f'November 2025 Targets: Airmass for All {len(df_november)} Targets\n' +
                  f'Centered on Midnight Hawaii Time (Middle of November 1 - December 1 window)',
                  fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=2, color='r', linestyle='--', alpha=0.3, label='Airmass = 2')
    
    plt.tight_layout()
    output_file = '../plots/november_airmass_all.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"   Saved: {output_file}")
    plt.close()
    
    # Display statistics
    print("\n" + "="*80)
    print("AIRMASS PLOTTING COMPLETE")
    print("="*80)
    print(f"Total targets plotted: {len(df_november)}")
    print(f"Observation date: {time.iso}")
    print(f"Output file: {output_file}")
    print(f"Brightest target: TIC{int(df_november_sorted.iloc[-1]['ticid'])} (V={df_november_sorted.iloc[-1]['v_mag']:.2f})")
    print(f"Faintest target: TIC{int(df_november_sorted.iloc[0]['ticid'])} (V={df_november_sorted.iloc[0]['v_mag']:.2f})")
    print("="*80)


if __name__ == "__main__":
    plot_november_airmass()
