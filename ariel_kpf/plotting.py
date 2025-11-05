"""
Plotting functions for ARIEL-KPF scheduling
Creates visualizations for target distribution and airmass curves
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
from astropy.time import Time
from astropy.coordinates import SkyCoord
import astropy.units as u
from astroplan import FixedTarget, Observer
from astroplan.plots import plot_airmass
from pathlib import Path

# Disable IERS auto-update (working offline)
from astropy.utils import iers
iers.conf.auto_max_age = None


def plot_target_distribution(df, strategies, strategy_name, output_file):
    """
    Create a sky plot showing all monthly targets.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with all KPF targets
    strategies : dict
        Dictionary of month configurations (from STRATEGIES)
    strategy_name : str
        Name of the strategy being plotted
    output_file : Path or str
        Output filename for the plot
    """
    print("\n📊 Creating target distribution plot...")
    
    # Create figure
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    ax1, ax2 = axes
    
    # Define colors for each month
    month_colors = {
        'nov': 'red',
        'dec': 'blue',
        'jan': 'green'
    }
    
    # Subplot 1: Full sky view
    all_month_targets = []
    for month_key, month_info in strategies.items():
        ra_min = month_info['ra_min']
        ra_max = month_info['ra_max']
        month_name = month_info['full_name']
        
        # Filter targets for this month
        month_mask = (df['ra'] >= ra_min) & (df['ra'] <= ra_max)
        df_month = df[month_mask].copy()
        all_month_targets.append(df_month)
        
        # Plot this month's targets
        color = month_colors.get(month_key, 'gray')
        scatter = ax1.scatter(df_month['ra'], df_month['dec'],
                            c=color, s=100, alpha=0.7,
                            edgecolors='black', linewidth=1,
                            label=f'{month_name} (RA {ra_min/15:.1f}-{ra_max/15:.1f}hr)',
                            zorder=2)
        
        # Highlight the RA range
        ax1.axvspan(ra_min, ra_max, alpha=0.1, color=color, zorder=0)
    
    # Plot other targets in gray
    all_scheduled = pd.concat(all_month_targets)
    other_mask = ~df.index.isin(all_scheduled.index)
    df_other = df[other_mask]
    if len(df_other) > 0:
        ax1.scatter(df_other['ra'], df_other['dec'],
                   c='lightgray', s=30, alpha=0.4,
                   edgecolors='gray', linewidth=0.5,
                   label='Not Scheduled', zorder=1)
    
    ax1.set_xlabel('Right Ascension (degrees)', fontsize=12)
    ax1.set_ylabel('Declination (degrees)', fontsize=12)
    ax1.set_title(f'Target Distribution: {strategy_name}', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best', framealpha=0.9, fontsize=10)
    ax1.set_xlim(0, 360)
    
    # Add secondary x-axis for hours
    ax1_top = ax1.twiny()
    ax1_top.set_xlim(0, 24)
    ax1_top.set_xlabel('Right Ascension (hours)', fontsize=12)
    
    # Subplot 2: V-magnitude vs RA
    for month_key, month_info in strategies.items():
        ra_min = month_info['ra_min']
        ra_max = month_info['ra_max']
        month_name = month_info['full_name']
        
        month_mask = (df['ra'] >= ra_min) & (df['ra'] <= ra_max)
        df_month = df[month_mask].copy()
        
        color = month_colors.get(month_key, 'gray')
        ax2.scatter(df_month['ra'], df_month['v_mag'],
                   c=color, s=80, alpha=0.7,
                   edgecolors='black', linewidth=1,
                   label=month_name)
    
    ax2.set_xlabel('Right Ascension (degrees)', fontsize=12)
    ax2.set_ylabel('V-magnitude', fontsize=12)
    ax2.set_title('Brightness Distribution', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best', framealpha=0.9)
    ax2.invert_yaxis()  # Brighter stars at top
    ax2.set_xlim(0, 360)
    
    # Add secondary x-axis for hours
    ax2_top = ax2.twiny()
    ax2_top.set_xlim(0, 24)
    ax2_top.set_xlabel('Right Ascension (hours)', fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✓ Saved to: {output_file}")


def plot_airmass_curves(df, strategies, strategy_name, output_file, year=2025):
    """
    Plot airmass curves for targets from all months.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with all KPF targets
    strategies : dict
        Dictionary of month configurations
    strategy_name : str
        Name of the strategy being plotted
    output_file : Path or str
        Output filename for the plot
    year : int
        Year for the observations (default: 2025)
    """
    print("\n📈 Creating airmass curves plot...")
    
    # Create Keck observer
    keck = Observer.at_site('Keck')
    
    # Create a figure with subplots for each month
    num_months = len(strategies)
    fig, axes = plt.subplots(1, num_months, figsize=(7*num_months, 6))
    if num_months == 1:
        axes = [axes]
    
    for ax, (month_key, month_info) in zip(axes, strategies.items()):
        ra_min = month_info['ra_min']
        ra_max = month_info['ra_max']
        month_name = month_info['full_name']
        start_date = month_info['start_date']
        
        # Filter targets for this month
        month_mask = (df['ra'] >= ra_min) & (df['ra'] <= ra_max)
        df_month = df[month_mask].copy()
        
        if len(df_month) == 0:
            continue
        
        # Use middle of the month for plotting
        obs_date = start_date.split('T')[0]
        time = Time(obs_date + ' 12:00')
        
        # Plot up to 10 targets to avoid overcrowding
        plot_count = min(10, len(df_month))
        df_plot = df_month.head(plot_count)
        
        for idx, row in df_plot.iterrows():
            ticid = int(row['ticid'])
            coord = SkyCoord(ra=row['ra']*u.deg, dec=row['dec']*u.deg)
            target = FixedTarget(coord=coord, name=f"TIC{ticid}")
            
            try:
                plot_airmass(target, keck, time, ax=ax, 
                           brightness_shading=True, 
                           altitude_yaxis=False)
            except:
                # Skip if airmass plot fails
                pass
        
        ax.set_title(f'{month_name} Targets\n(RA {ra_min/15:.1f}-{ra_max/15:.1f}hr)', 
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Time (hours from midnight)', fontsize=10)
        ax.set_ylabel('Airmass', fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc='upper right', ncol=2)
        
        # Add note about number of targets
        total_targets = len(df_month)
        if plot_count < total_targets:
            ax.text(0.02, 0.98, f'Showing {plot_count}/{total_targets} targets',
                   transform=ax.transAxes, fontsize=8, va='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    fig.suptitle(f'Airmass Curves: {strategy_name}', fontsize=16, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✓ Saved to: {output_file}")


def generate_all_plots(df, strategies, strategy_name, plots_dir):
    """
    Generate all plots for the observing strategy.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame with all KPF targets
    strategies : dict
        Dictionary of month configurations
    strategy_name : str
        Name of the strategy
    plots_dir : Path
        Directory to save plots
    """
    print("\n" + "="*60)
    print("GENERATING PLOTS")
    print("="*60)
    
    # Ensure plots directory exists
    plots_dir = Path(plots_dir)
    plots_dir.mkdir(exist_ok=True)
    
    # Generate target distribution plot
    dist_file = plots_dir / f'{strategy_name}_target_distribution.png'
    try:
        plot_target_distribution(df, strategies, strategy_name, dist_file)
    except Exception as e:
        print(f"   ⚠ Error creating distribution plot: {e}")
    
    # Generate airmass curves plot
    airmass_file = plots_dir / f'{strategy_name}_airmass.png'
    try:
        plot_airmass_curves(df, strategies, strategy_name, airmass_file)
    except Exception as e:
        print(f"   ⚠ Error creating airmass plot: {e}")
    
    print("="*60)

