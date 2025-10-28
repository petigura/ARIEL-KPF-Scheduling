#!/usr/bin/env python3
"""
Generate Observing Blocks (OBs) for November 2025
Filters targets with RA = 20-24 hr (300-360 degrees) and creates JSON OBs
"""

import pandas as pd
import json
import copy
from astropy.coordinates import SkyCoord
from astropy import units as u

def load_template():
    """
    Load the OB template from ob-template.json.
    Strips comments (lines starting with # or content after #).
    
    Returns:
    --------
    dict : The template OB as a dictionary
    """
    print("Loading OB template...")
    with open('../obs/ob-template.json', 'r') as f:
        json_content = f.read()
        
        # Remove inline comments (everything after # on each line)
        lines = json_content.split('\n')
        cleaned_lines = []
        for line in lines:
            if '#' in line:
                # Find the position of # and strip everything after it
                cleaned_line = line.split('#')[0].rstrip()
                cleaned_lines.append(cleaned_line)
            else:
                cleaned_lines.append(line)
        
        cleaned_json = '\n'.join(cleaned_lines)
        template_data = json.loads(cleaned_json)
        template_ob = template_data[0]  # Get first (and only) OB from array
    
    print(f"✓ Template loaded successfully")
    return template_ob

def load_kpf_targets():
    """
    Load KPF target data from CSV file.
    
    Returns:
    --------
    pandas.DataFrame : DataFrame containing target information
    """
    print("\nLoading KPF target data...")
    df = pd.read_csv('../targets/ariel_kpf_targets_20251016_162105.csv')
    print(f"✓ Loaded {len(df)} KPF targets")
    return df

def filter_november_targets(df):
    """
    Filter targets for November observing window (RA = 20-24 hr = 300-360 degrees).
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
        
    Returns:
    --------
    pandas.DataFrame : Filtered DataFrame with November targets
    """
    print("\nFiltering targets for November (RA = 20-24 hr)...")
    
    # Filter for RA between 300 and 360 degrees (20-24 hours)
    df_november = df[(df['ra'] >= 300) & (df['ra'] <= 360)].copy()
    
    # Sort by RA for better organization
    df_november = df_november.sort_values('ra')
    
    print(f"✓ Found {len(df_november)} targets in November window")
    print(f"  RA range: {df_november['ra'].min():.2f}° to {df_november['ra'].max():.2f}°")
    
    return df_november

def create_ob_for_target(target_row, template_ob):
    """
    Create an Observing Block (OB) for a single target.
    
    Parameters:
    -----------
    target_row : pandas.Series
        Row from DataFrame containing target information
    template_ob : dict
        Template OB structure
        
    Returns:
    --------
    dict : Complete OB for the target
    """
    # Create a deep copy of the template
    ob = copy.deepcopy(template_ob)
    
    # Extract target information
    ticid = int(target_row['ticid'])
    ra_deg = target_row['ra']
    dec_deg = target_row['dec']
    
    # Convert coordinates to sexagesimal format
    coord = SkyCoord(ra=ra_deg*u.deg, dec=dec_deg*u.deg, frame='icrs')
    ra_str = coord.ra.to_string(unit=u.hourangle, sep=':', precision=2, pad=True)
    dec_str = coord.dec.to_string(unit=u.deg, sep=':', precision=2, pad=True)
    
    # Update target section
    target_name = f"TIC{ticid}"
    ob['target']['TargetName'] = target_name
    ob['target']['tic_id'] = str(ticid)
    ob['target']['RA'] = ra_str
    ob['target']['DEC'] = dec_str
    ob['target']['ra_deg'] = float(ra_deg)
    ob['target']['dec_deg'] = float(dec_deg)
    
    # Update observation section - ensure Object matches TargetName
    ob['observation']['Object'] = target_name
    
    # Update schedule section with November-December 2025 time constraints
    ob['schedule']['custom_time_constraints'] = [
        {
            "start_datetime": "2025-11-01T12:00",
            "end_datetime": "2025-12-01T12:00"
        }
    ]
    
    # Remove fields that will be updated by KPF-CC webpage
    if 'total_observations_requested' in ob['schedule']:
        del ob['schedule']['total_observations_requested']
    if 'total_time_for_target' in ob['schedule']:
        del ob['schedule']['total_time_for_target']
    if 'total_time_for_target_hours' in ob['schedule']:
        del ob['schedule']['total_time_for_target_hours']
    
    # Ensure metadata section exists as empty dict
    if 'metadata' not in ob:
        ob['metadata'] = {}
    
    return ob

def generate_november_obs():
    """
    Main function to generate November observing blocks.
    Creates two output files:
    - obs_november_2025.json: All November targets
    - obs_november_2025_test.json: First 2 targets for testing
    """
    print("="*60)
    print("GENERATING NOVEMBER 2025 OBSERVING BLOCKS")
    print("="*60)
    
    # Load template and target data
    template_ob = load_template()
    df = load_kpf_targets()
    
    # Filter for November targets
    df_november = filter_november_targets(df)
    
    if len(df_november) == 0:
        print("\n❌ No targets found for November window!")
        return
    
    # Generate OBs for all November targets
    print("\nGenerating OBs...")
    obs_list = []
    for idx, row in df_november.iterrows():
        ob = create_ob_for_target(row, template_ob)
        obs_list.append(ob)
        print(f"  ✓ Created OB for TIC{int(row['ticid'])} (RA={row['ra']:.2f}°)")
    
    # Save full list
    output_file_full = '../obs/obs_november_2025.json'
    with open(output_file_full, 'w') as f:
        json.dump(obs_list, f, indent=2)
    print(f"\n✅ Saved {len(obs_list)} OBs to: {output_file_full}")
    
    # Save test file (first 2 targets)
    output_file_test = '../obs/obs_november_2025_test.json'
    test_obs_list = obs_list[:2]
    with open(output_file_test, 'w') as f:
        json.dump(test_obs_list, f, indent=2)
    print(f"✅ Saved {len(test_obs_list)} test OBs to: {output_file_test}")
    
    # Display summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total November targets: {len(obs_list)}")
    print(f"Observation window: November 1 - December 1, 2025")
    print(f"RA range: {df_november['ra'].min():.2f}° to {df_november['ra'].max():.2f}° (20-24 hr)")
    print(f"\nOutput files:")
    print(f"  • {output_file_full} - All {len(obs_list)} targets")
    print(f"  • {output_file_test} - First {len(test_obs_list)} targets (for testing)")
    print("="*60)

if __name__ == "__main__":
    generate_november_obs()
