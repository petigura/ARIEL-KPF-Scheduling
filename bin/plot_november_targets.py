#!/usr/bin/env python3
"""
Plot November targets in context with all KPF targets
Shows which targets are scheduled for November 2025 (RA 300-360°)
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

def plot_november_targets():
    """
    Create a sky plot showing November targets highlighted among all KPF targets.
    """
    print("="*80)
    print("Plotting November Targets in Context")
    print("="*80)
    
    # Load target data
    print("\n1. Loading target data...")
    csv_file = "../targets/ariel_kpf_targets_20251016_162105.csv"
    df = pd.read_csv(csv_file)
    
    # Filter for KPF targets only
    df_kpf = df[df['observe_kpf'] == True].copy()
    print(f"   Total KPF targets: {len(df_kpf)}")
    
    # Identify November targets (RA 300-360°)
    november_mask = (df_kpf['ra'] >= 300) & (df_kpf['ra'] <= 360)
    df_november = df_kpf[november_mask].copy()
    df_other = df_kpf[~november_mask].copy()
    
    print(f"   November targets (RA 300-360°): {len(df_november)}")
    print(f"   Other targets: {len(df_other)}")
    
    # Create figure with two subplots
    fig = plt.figure(figsize=(16, 6))
    
    # Subplot 1: Full sky view
    ax1 = plt.subplot(1, 2, 1)
    
    # Plot all other targets in gray
    ax1.scatter(df_other['ra'], df_other['dec'], 
               c='lightgray', s=50, alpha=0.6, 
               edgecolors='gray', linewidth=0.5,
               label='Other KPF Targets', zorder=1)
    
    # Plot November targets in color
    scatter = ax1.scatter(df_november['ra'], df_november['dec'],
                         c=df_november['v_mag'], s=100, alpha=0.8,
                         cmap='plasma_r', edgecolors='black', linewidth=1,
                         label='November Targets (RA 20-24hr)', zorder=2)
    
    # Add colorbar for V-magnitude
    cbar = plt.colorbar(scatter, ax=ax1, label='V-magnitude')
    
    # Highlight the November RA range
    ax1.axvspan(300, 360, alpha=0.15, color='blue', zorder=0)
    ax1.text(330, ax1.get_ylim()[1] * 0.95, 'November\nRA Range\n(20-24 hr)', 
            ha='center', va='top', fontsize=10, 
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    ax1.set_xlabel('Right Ascension (degrees)', fontsize=12)
    ax1.set_ylabel('Declination (degrees)', fontsize=12)
    ax1.set_title('November Targets in Context: Full Sky View', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', framealpha=0.9)
    ax1.set_xlim(0, 360)
    
    # Add secondary x-axis for hours
    ax1_top = ax1.twiny()
    ax1_top.set_xlim(0, 24)
    ax1_top.set_xlabel('Right Ascension (hours)', fontsize=12)
    
    # Subplot 2: Zoomed view of November targets
    ax2 = plt.subplot(1, 2, 2)
    
    # Plot November targets with labels
    scatter2 = ax2.scatter(df_november['ra'], df_november['dec'],
                          c=df_november['v_mag'], s=150, alpha=0.8,
                          cmap='plasma_r', edgecolors='black', linewidth=1.5)
    
    # Add colorbar
    cbar2 = plt.colorbar(scatter2, ax=ax2, label='V-magnitude')
    
    # Label brightest targets
    df_november_sorted = df_november.sort_values('v_mag')
    for idx, row in df_november_sorted.head(5).iterrows():
        ticid = int(row['ticid'])
        ax2.annotate(f'TIC{ticid}', 
                    xy=(row['ra'], row['dec']),
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=8, alpha=0.7,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
    
    ax2.set_xlabel('Right Ascension (degrees)', fontsize=12)
    ax2.set_ylabel('Declination (degrees)', fontsize=12)
    ax2.set_title('November Targets: Zoomed View (RA 300-360°)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(295, 365)
    
    # Add secondary x-axis for hours
    ax2_top = ax2.twiny()
    ax2_top.set_xlim(295/15, 365/15)
    ax2_top.set_xlabel('Right Ascension (hours)', fontsize=12)
    
    plt.tight_layout()
    
    # Save figure
    output_file = 'plots/november_targets_context.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n2. Plot saved to: {output_file}")
    plt.close()
    
    # Display statistics
    print("\n" + "="*80)
    print("STATISTICS")
    print("="*80)
    print(f"Total KPF targets: {len(df_kpf)}")
    print(f"November targets (RA 20-24 hr): {len(df_november)} ({len(df_november)/len(df_kpf)*100:.1f}%)")
    print(f"\nNovember targets V-mag range: {df_november['v_mag'].min():.2f} - {df_november['v_mag'].max():.2f}")
    print(f"November targets DEC range: {df_november['dec'].min():.1f}° to {df_november['dec'].max():.1f}°")
    print("="*80)


if __name__ == "__main__":
    plot_november_targets()

