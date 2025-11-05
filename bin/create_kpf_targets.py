#!/usr/bin/env python3
"""
Create filtered CSV with only KPF targets for analysis
Includes bulk SIMBAD queries to populate target metadata
"""

import pandas as pd
import time
from datetime import datetime
from astroquery.simbad import Simbad
from ariel_kpf.paths import TARGETS_DIR, get_latest_targets_file

def query_simbad_bulk(ticids):
    """
    Query SIMBAD for multiple targets at once.
    
    Parameters:
    -----------
    ticids : list or array
        List of TIC IDs to query
        
    Returns:
    --------
    dict : Dictionary mapping TIC IDs to SIMBAD data
    """
    print(f"\nQuerying SIMBAD for {len(ticids)} targets...")
    print("This may take a few minutes...")
    
    # Configure SIMBAD query
    custom_simbad = Simbad()
    custom_simbad.add_votable_fields('ids', 'parallax', 'pmra', 'pmdec', 'G', 'J', 'rvz_radvel')
    
    # Map SIMBAD column names to our field names
    field_mapping = {
        'plx_value': ('parallax', float),
        'pmra': ('pmra', float),
        'pmdec': ('pmdec', float),
        'G': ('gmag', float),
        'J': ('jmag', float),
        'rvz_radvel': ('radial_velocity', float),
    }
    
    # Initialize results dictionary
    results = {}
    
    # Query in batches
    batch_size = 50
    total_batches = (len(ticids) + batch_size - 1) // batch_size
    
    for i in range(0, len(ticids), batch_size):
        batch = ticids[i:i+batch_size]
        batch_num = i // batch_size + 1
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} targets)...", end='', flush=True)
        
        # Create TIC names for query
        tic_names = [f"TIC {ticid}" for ticid in batch]
        
        try:
            result_table = custom_simbad.query_objects(tic_names)
            
            if result_table is None or len(result_table) == 0:
                print(f" No results")
                for ticid in batch:
                    results[ticid] = {}
                continue
            
            # Process results
            for ticid in batch:
                tic_name = f"TIC {ticid}"
                # Find matching row by user_specified_id column
                matching_rows = [k for k, row in enumerate(result_table) 
                               if 'user_specified_id' in row.colnames and tic_name in str(row['user_specified_id'])]
                
                if not matching_rows:
                    results[ticid] = {}
                    continue
                
                row = result_table[matching_rows[0]]
                simbad_data = {}
                
                # Extract IDs from the ids field (keep as strings)
                if 'ids' in row.colnames and row['ids']:
                    ids_list = row['ids'].split('|')
                    for id_item in ids_list:
                        if 'Gaia DR3' in id_item:
                            # Keep as string to preserve full precision
                            simbad_data['gaia_dr3_id'] = str(id_item.strip().replace('Gaia DR3 ', ''))
                        elif '2MASS J' in id_item:
                            simbad_data['twomass_id'] = str(id_item.strip().replace('2MASS J', ''))
                
                # Extract other fields
                for simbad_col, (our_field, dtype) in field_mapping.items():
                    if simbad_col in row.colnames and row[simbad_col] is not None:
                        try:
                            simbad_data[our_field] = dtype(row[simbad_col])
                        except:
                            pass
                
                results[ticid] = simbad_data
            
            print(f" ✓ {len(result_table)} found")
            time.sleep(0.5)  # Respect SIMBAD rate limits
            
        except Exception as e:
            print(f" ⚠ Error: {e}")
            for ticid in batch:
                results[ticid] = {}
    
    # Count how many targets have data
    found = sum(1 for data in results.values() if data)
    print(f"\n✓ SIMBAD queries complete: {found}/{len(ticids)} targets found")
    
    return results

def create_kpf_targets_csv():
    """Create a CSV file containing only KPF targets."""
    
    print("Creating KPF targets CSV...")
    
    # Read the full dataset (use latest file)
    latest_file = get_latest_targets_file()
    if latest_file is None:
        print("❌ No ARIEL targets file found!")
        print(f"Please run download_ariel_data.py first or place a file in {TARGETS_DIR}")
        return None, None
    
    print(f"Reading: {latest_file.name}")
    df = pd.read_csv(latest_file)
    
    # Filter for KPF targets only
    kpf_targets = df[df['observe_kpf'] == True].copy()
    
    print(f"Original dataset: {len(df)} targets")
    print(f"KPF targets: {len(kpf_targets)} targets")
    
    # Query SIMBAD for all KPF targets
    ticids = kpf_targets['ticid'].tolist()
    simbad_results = query_simbad_bulk(ticids)
    
    # Add SIMBAD data as new columns
    print("\nAdding SIMBAD data to dataframe...")
    simbad_columns = ['gaia_dr3_id', 'twomass_id', 'parallax', 'pmra', 'pmdec', 
                      'gmag', 'jmag', 'radial_velocity']
    
    for col in simbad_columns:
        kpf_targets[col] = kpf_targets['ticid'].apply(
            lambda ticid: simbad_results.get(ticid, {}).get(col, None)
        )
    
    # Count how many targets have each field
    print("\nSIMBAD data coverage:")
    for col in simbad_columns:
        count = kpf_targets[col].notna().sum()
        pct = 100 * count / len(kpf_targets)
        print(f"  {col}: {count}/{len(kpf_targets)} ({pct:.1f}%)")
    
    # Save KPF targets to separate CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = TARGETS_DIR / f"ariel_kpf_targets_{timestamp}.csv"
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
