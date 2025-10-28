#!/usr/bin/env python3
"""
Create filtered CSV with only KPF targets for analysis
"""

import pandas as pd
from datetime import datetime

def create_kpf_targets_csv():
    """Create a CSV file containing only KPF targets."""
    
    print("Creating KPF targets CSV...")
    
    # Read the full dataset
    df = pd.read_csv('../targets/ariel_targets_20251016_161910.csv')
    
    # Filter for KPF targets only
    kpf_targets = df[df['observe_kpf'] == True].copy()
    
    print(f"Original dataset: {len(df)} targets")
    print(f"KPF targets: {len(kpf_targets)} targets")
    
    # Save KPF targets to separate CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"../targets/ariel_kpf_targets_{timestamp}.csv"
    kpf_targets.to_csv(filename, index=False)
    
    print(f"✅ KPF targets saved to: {filename}")
    
    # Display summary statistics
    print("\n" + "="*60)
    print("KPF TARGETS SUMMARY")
    print("="*60)
    print(f"Total KPF targets: {len(kpf_targets)}")
    
    # Coordinate ranges
    print(f"\nCoordinate ranges:")
    print(f"  RA: {kpf_targets['ra'].min():.3f}° to {kpf_targets['ra'].max():.3f}°")
    print(f"  DEC: {kpf_targets['dec'].min():.3f}° to {kpf_targets['dec'].max():.3f}°")
    
    # Magnitude ranges
    v_mag_data = kpf_targets['v_mag'].dropna()
    tess_mag_data = kpf_targets['tess_mag'].dropna()
    
    if len(v_mag_data) > 0:
        print(f"  V magnitude: {v_mag_data.min():.2f} to {v_mag_data.max():.2f}")
    if len(tess_mag_data) > 0:
        print(f"  TESS magnitude: {tess_mag_data.min():.2f} to {tess_mag_data.max():.2f}")
    
    # Planet properties
    radius_data = kpf_targets['planet_radius'].dropna()
    period_data = kpf_targets['period'].dropna()
    
    if len(radius_data) > 0:
        print(f"  Planet radius: {radius_data.min():.2f} to {radius_data.max():.2f} Earth radii")
    if len(period_data) > 0:
        print(f"  Planet period: {period_data.min():.3f} to {period_data.max():.3f} days")
    
    # Stellar properties
    teff_data = kpf_targets['stellar_teff'].dropna()
    distance_data = kpf_targets['stellar_distance'].dropna()
    
    if len(teff_data) > 0:
        print(f"  Stellar Teff: {teff_data.min():.0f} to {teff_data.max():.0f} K")
    if len(distance_data) > 0:
        print(f"  Stellar distance: {distance_data.min():.1f} to {distance_data.max():.1f} pc")
    
    # Show first few targets
    print(f"\nFirst 5 KPF targets:")
    print(kpf_targets[['ticid', 'ra', 'dec', 'v_mag', 'planet_radius', 'period']].head().to_string(index=False))
    
    return kpf_targets, filename

def main():
    print("ARIEL-KPF Targets Filtering")
    print("=" * 40)
    
    kpf_targets, filename = create_kpf_targets_csv()
    
    if kpf_targets is not None:
        print(f"\n✅ Successfully created KPF targets file!")
        print(f"📁 File: {filename}")
        print(f"📊 Contains {len(kpf_targets)} KPF targets")
        print(f"🎯 Ready for AstroQ analysis!")
    else:
        print("\n❌ Failed to create KPF targets file!")

if __name__ == "__main__":
    main()
