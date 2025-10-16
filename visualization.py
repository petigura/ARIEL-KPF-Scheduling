#!/usr/bin/env python3
"""
ARIEL-KPF Scheduling Tool - Visualization Module
Creates plots for target analysis and scheduling.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from astropy.coordinates import SkyCoord
from astropy import units as u
import matplotlib.patches as patches
from matplotlib.patches import Circle
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib style for better plots
plt.style.use('default')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


def create_sky_plot(df, save_path=None):
    """
    Create a sky plot showing target distribution in RA/DEC coordinates.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    save_path : str, optional
        Path to save the plot
    """
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Extract RA and DEC
    ra = df['ra'].values
    dec = df['dec'].values
    
    # Create scatter plot
    scatter = ax.scatter(ra, dec, c=df['v_mag'], cmap='viridis', 
                        s=50, alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('V-magnitude', fontsize=12)
    
    # Customize plot
    ax.set_xlabel('Right Ascension (degrees)', fontsize=12)
    ax.set_ylabel('Declination (degrees)', fontsize=12)
    ax.set_title('ARIEL-KPF Target Distribution on Sky\n(377 targets)', fontsize=14, fontweight='bold')
    
    # Invert RA axis (astronomical convention)
    ax.invert_xaxis()
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add Keck Observatory location (approximate)
    keck_ra = 204.5  # Approximate RA of Keck Observatory
    keck_dec = 19.8  # Approximate DEC of Keck Observatory
    ax.plot(keck_ra, keck_dec, 'r*', markersize=15, label='Keck Observatory')
    
    # Add legend
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Sky plot saved to: {save_path}")
    
    plt.show()


def create_magnitude_histogram(df, save_path=None):
    """
    Create histogram of target magnitudes.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    save_path : str, optional
        Path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # V-magnitude histogram
    ax1.hist(df['v_mag'].dropna(), bins=30, alpha=0.7, color='blue', edgecolor='black')
    ax1.set_xlabel('V-magnitude', fontsize=12)
    ax1.set_ylabel('Number of Targets', fontsize=12)
    ax1.set_title('V-magnitude Distribution', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # TESS magnitude histogram
    ax2.hist(df['tess_mag'].dropna(), bins=30, alpha=0.7, color='red', edgecolor='black')
    ax2.set_xlabel('TESS-magnitude', fontsize=12)
    ax2.set_ylabel('Number of Targets', fontsize=12)
    ax2.set_title('TESS-magnitude Distribution', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle('Target Magnitude Distributions', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Magnitude histogram saved to: {save_path}")
    
    plt.show()


def create_period_radius_plot(df, save_path=None):
    """
    Create scatter plot of planetary period vs radius.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    save_path : str, optional
        Path to save the plot
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Filter out invalid data
    valid_data = df.dropna(subset=['period', 'planet_radius'])
    valid_data = valid_data[(valid_data['period'] > 0) & (valid_data['planet_radius'] > 0)]
    
    # Create scatter plot colored by V-magnitude
    scatter = ax.scatter(valid_data['period'], valid_data['planet_radius'], 
                       c=valid_data['v_mag'], cmap='plasma', 
                       s=60, alpha=0.7, edgecolors='black', linewidth=0.5)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('V-magnitude', fontsize=12)
    
    # Customize plot
    ax.set_xlabel('Orbital Period (days)', fontsize=12)
    ax.set_ylabel('Planet Radius (Earth radii)', fontsize=12)
    ax.set_title('Planetary Period vs Radius\n(Colored by V-magnitude)', fontsize=14, fontweight='bold')
    
    # Use log scale for better visualization
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # Add grid
    ax.grid(True, alpha=0.3)
    
    # Add reference lines for common planet types
    ax.axhline(y=1, color='green', linestyle='--', alpha=0.5, label='Earth radius')
    ax.axhline(y=4, color='blue', linestyle='--', alpha=0.5, label='Neptune radius')
    ax.axhline(y=11, color='red', linestyle='--', alpha=0.5, label='Jupiter radius')
    
    ax.legend(fontsize=10)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Period-radius plot saved to: {save_path}")
    
    plt.show()


def create_stellar_parameter_plot(df, save_path=None):
    """
    Create plots of stellar parameters.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    save_path : str, optional
        Path to save the plot
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Teff vs logg
    valid_data = df.dropna(subset=['stellar_teff', 'stellar_logg'])
    scatter1 = ax1.scatter(valid_data['stellar_teff'], valid_data['stellar_logg'], 
                         c=valid_data['v_mag'], cmap='viridis', s=50, alpha=0.7)
    ax1.set_xlabel('Effective Temperature (K)', fontsize=12)
    ax1.set_ylabel('Surface Gravity (log g)', fontsize=12)
    ax1.set_title('Stellar Teff vs log g', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label='V-magnitude')
    
    # Distance vs Teff
    valid_data2 = df.dropna(subset=['stellar_distance', 'stellar_teff'])
    scatter2 = ax2.scatter(valid_data2['stellar_distance'], valid_data2['stellar_teff'], 
                          c=valid_data2['v_mag'], cmap='plasma', s=50, alpha=0.7)
    ax2.set_xlabel('Distance (pc)', fontsize=12)
    ax2.set_ylabel('Effective Temperature (K)', fontsize=12)
    ax2.set_title('Distance vs Teff', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    plt.colorbar(scatter2, ax=ax2, label='V-magnitude')
    
    # Stellar radius histogram
    ax3.hist(df['stellar_radius'].dropna(), bins=30, alpha=0.7, color='orange', edgecolor='black')
    ax3.set_xlabel('Stellar Radius (Solar radii)', fontsize=12)
    ax3.set_ylabel('Number of Targets', fontsize=12)
    ax3.set_title('Stellar Radius Distribution', fontsize=12, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # Distance histogram
    ax4.hist(df['stellar_distance'].dropna(), bins=30, alpha=0.7, color='purple', edgecolor='black')
    ax4.set_xlabel('Distance (pc)', fontsize=12)
    ax4.set_ylabel('Number of Targets', fontsize=12)
    ax4.set_title('Distance Distribution', fontsize=12, fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Stellar Parameter Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Stellar parameter plot saved to: {save_path}")
    
    plt.show()


def create_observation_priority_plot(df, save_path=None):
    """
    Create plots showing observation priorities and flags.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    save_path : str, optional
        Path to save the plot
    """
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # KPF observation flags
    kpf_counts = df['observe_kpf'].value_counts()
    ax1.pie(kpf_counts.values, labels=kpf_counts.index, autopct='%1.1f%%', startangle=90)
    ax1.set_title('KPF Observation Flags', fontsize=12, fontweight='bold')
    
    # NEID observation flags
    neid_counts = df['observe_neid'].value_counts()
    ax2.pie(neid_counts.values, labels=neid_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.set_title('NEID Observation Flags', fontsize=12, fontweight='bold')
    
    # V-magnitude vs observation priority
    kpf_targets = df[df['observe_kpf'] == True]
    neid_targets = df[df['observe_neid'] == True]
    
    ax3.scatter(kpf_targets['v_mag'], kpf_targets['period'], 
               c='blue', s=50, alpha=0.7, label='KPF targets', edgecolors='black')
    ax3.scatter(neid_targets['v_mag'], neid_targets['period'], 
               c='red', s=50, alpha=0.7, label='NEID targets', edgecolors='black')
    ax3.set_xlabel('V-magnitude', fontsize=12)
    ax3.set_ylabel('Period (days)', fontsize=12)
    ax3.set_title('Observation Priority by Instrument', fontsize=12, fontweight='bold')
    ax3.set_yscale('log')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Target count by semester
    semester_cols = ['observed_in_2025b', 'observed_in_2026a', 'observed_in_2027a', 'observed_in_2027b']
    semester_counts = []
    semester_labels = []
    
    for col in semester_cols:
        if col in df.columns:
            count = df[col].notna().sum()
            semester_counts.append(count)
            semester_labels.append(col.replace('observed_in_', ''))
    
    ax4.bar(semester_labels, semester_counts, color=['skyblue', 'lightgreen', 'lightcoral', 'lightyellow'])
    ax4.set_xlabel('Semester', fontsize=12)
    ax4.set_ylabel('Number of Targets', fontsize=12)
    ax4.set_title('Targets by Observation Semester', fontsize=12, fontweight='bold')
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle('Observation Priority and Scheduling Analysis', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Observation priority plot saved to: {save_path}")
    
    plt.show()


def create_all_plots(df, output_dir='plots'):
    """
    Create all visualization plots and save them to a directory.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    output_dir : str
        Directory to save plots
    """
    import os
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("Creating visualization plots for ARIEL-KPF targets...")
    print(f"Saving plots to: {output_dir}/")
    print()
    
    # Create all plots
    create_sky_plot(df, f"{output_dir}/sky_distribution.png")
    create_magnitude_histogram(df, f"{output_dir}/magnitude_distributions.png")
    create_period_radius_plot(df, f"{output_dir}/period_radius_plot.png")
    create_stellar_parameter_plot(df, f"{output_dir}/stellar_parameters.png")
    create_observation_priority_plot(df, f"{output_dir}/observation_priority.png")
    
    print("\n✅ All plots created successfully!")
    print(f"📁 Plots saved in: {output_dir}/")


if __name__ == "__main__":
    # This will be imported and used by main.py
    print("Visualization module loaded. Use create_all_plots(df) to generate plots.")
