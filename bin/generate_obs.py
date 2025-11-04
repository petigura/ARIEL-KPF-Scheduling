#!/usr/bin/env python3
"""
Generate Observing Blocks (OBs) for KPF observations (2025B semester)
Filters targets by month-appropriate RA range and creates JSON OBs
Supports: November, December, January
"""

import pandas as pd
import json
import copy
import argparse
from astropy.coordinates import SkyCoord
from astropy import units as u
from ariel_kpf.paths import TARGETS_DIR, OBS_DIR, OB_TEMPLATE, get_latest_kpf_targets_file

# Hard-coded year for this observing semester
YEAR = 2025

# Observing strategies - nested dictionary: STRATEGIES[version][month]
STRATEGIES = {
    'version1': {
        'nov': {
            'ra_min': 300, 
            'ra_max': 360, 
            'full_name': 'November',
            'start_date': '2025-11-01T12:00',
            'end_date': '2025-12-01T12:00'
        },
        'dec': {
            'ra_min': 0, 
            'ra_max': 60, 
            'full_name': 'December',
            'start_date': '2025-12-01T12:00',
            'end_date': '2026-01-01T12:00'
        },
        'jan': {
            'ra_min': 60, 
            'ra_max': 120, 
            'full_name': 'January',
            'start_date': '2026-01-01T12:00',
            'end_date': '2026-02-01T12:00'
        }
    }
}

def load_template():
    """
    Load the OB template from ob-template.json.
    Strips comments (lines starting with # or content after #).
    
    Returns:
    --------
    dict : The template OB as a dictionary
    """
    print("Loading OB template...")
    with open(OB_TEMPLATE, 'r') as f:
        json_content = f.read()
        
        # Remove inline comments (everything after # on each line)
        lines = json_content.split('\n')
        cleaned_lines = []
        for line in lines:
            if '#' in line:
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
    
    # Use the latest KPF targets file
    latest_file = get_latest_kpf_targets_file()
    if latest_file is None:
        print(f"❌ No KPF targets file found in {TARGETS_DIR}")
        print("Please run create_kpf_targets.py first")
        raise FileNotFoundError("No KPF targets file found")
    
    print(f"Reading: {latest_file.name}")
    df = pd.read_csv(latest_file)
    print(f"✓ Loaded {len(df)} KPF targets")
    return df

def filter_targets_by_ra(df, ra_min, ra_max):
    """
    Filter targets by RA range.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame containing target information
    ra_min : float
        Minimum RA in degrees
    ra_max : float
        Maximum RA in degrees
        
    Returns:
    --------
    pandas.DataFrame : Filtered DataFrame with targets in RA range
    """
    print(f"\nFiltering targets for RA range {ra_min}° to {ra_max}° ({ra_min/15:.1f}-{ra_max/15:.1f} hr)...")
    
    # Filter for RA between ra_min and ra_max degrees
    df_filtered = df[(df['ra'] >= ra_min) & (df['ra'] <= ra_max)].copy()
    
    # Sort by RA for better organization
    df_filtered = df_filtered.sort_values('ra')
    
    print(f"✓ Found {len(df_filtered)} targets in window")
    if len(df_filtered) > 0:
        print(f"  RA range: {df_filtered['ra'].min():.2f}° to {df_filtered['ra'].max():.2f}°")
    
    return df_filtered

def create_ob_for_target(target_row, template_ob, start_date, end_date):
    """
    Create an Observing Block (OB) for a single target.
    
    Parameters:
    -----------
    target_row : pandas.Series
        Row from DataFrame containing target information
    template_ob : dict
        Template OB structure
    start_date : str
        Start date in format "YYYY-MM-DDTHH:MM"
    end_date : str
        End date in format "YYYY-MM-DDTHH:MM"
        
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
    
    # Update observation parameters from target data
    if 't_sec_kpf' in target_row.index and not pd.isna(target_row['t_sec_kpf']):
        ob['observation']['ExpTime'] = str(int(target_row['t_sec_kpf'] * 4)) # multiply by 4 to account for upto 4x slowdown
    
    if 'expmeter_kpf' in target_row.index and not pd.isna(target_row['expmeter_kpf']):
        ob['observation']['ExpMeterThreshold'] = target_row['expmeter_kpf']
    
    # Update schedule section with time constraints
    ob['schedule']['custom_time_constraints'] = [
        {
            "start_datetime": start_date,
            "end_datetime": end_date
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

def generate_obs(month, strategy='version1', num_test_targets=2):
    """
    Main function to generate observing blocks for a specific month using a strategy.
    
    Parameters:
    -----------
    month : str
        Month abbreviation ('nov', 'dec', 'jan')
    strategy : str
        Strategy version to use (default: 'version1')
    num_test_targets : int
        Number of targets to include in test file
    """
    month = month.lower()
    
    # Validate strategy
    if strategy not in STRATEGIES:
        print(f"❌ Error: Invalid strategy '{strategy}'")
        print(f"Valid strategies: {', '.join(STRATEGIES.keys())}")
        return
    
    # Validate month for this strategy
    if month not in STRATEGIES[strategy]:
        print(f"❌ Error: Invalid month '{month}' for strategy '{strategy}'")
        print(f"Valid months for {strategy}: {', '.join(STRATEGIES[strategy].keys())}")
        return
    
    month_info = STRATEGIES[strategy][month]
    month_full = month_info['full_name']
    
    print("="*60)
    print(f"GENERATING {month_full.upper()} {YEAR} OBSERVING BLOCKS")
    print(f"Strategy: {strategy}")
    print("="*60)
    
    # Load template and target data
    template_ob = load_template()
    df = load_kpf_targets()
    
    # Get RA range and time window for this month
    ra_min = month_info['ra_min']
    ra_max = month_info['ra_max']
    start_date = month_info['start_date']
    end_date = month_info['end_date']
    
    # Filter targets by RA range
    df_filtered = filter_targets_by_ra(df, ra_min, ra_max)
    
    if len(df_filtered) == 0:
        print(f"\n❌ No targets found for {month_full} window!")
        return
    
    # Generate OBs for all filtered targets
    print("\nGenerating OBs...")
    obs_list = []
    for idx, row in df_filtered.iterrows():
        ob = create_ob_for_target(row, template_ob, start_date, end_date)
        obs_list.append(ob)
        print(f"  ✓ Created OB for TIC{int(row['ticid'])} (RA={row['ra']:.2f}°)")
    
    # Save full list
    output_file_full = OBS_DIR / f'obs_{month}_{YEAR}.json'
    with open(output_file_full, 'w') as f:
        json.dump(obs_list, f, indent=2)
    print(f"\n✅ Saved {len(obs_list)} OBs to: {output_file_full}")
    
    # Save test file
    output_file_test = OBS_DIR / f'obs_{month}_{YEAR}_test.json'
    test_obs_list = obs_list[:num_test_targets]
    with open(output_file_test, 'w') as f:
        json.dump(test_obs_list, f, indent=2)
    print(f"✅ Saved {len(test_obs_list)} test OBs to: {output_file_test}")
    
    # Display summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Strategy: {strategy}")
    print(f"Month: {month_full}")
    print(f"Total targets: {len(obs_list)}")
    print(f"Observation window: {start_date} to {end_date}")
    print(f"RA range: {ra_min}° to {ra_max}° ({ra_min/15:.1f}-{ra_max/15:.1f} hr)")
    print(f"\nOutput files:")
    print(f"  • {output_file_full} - All {len(obs_list)} targets")
    print(f"  • {output_file_test} - First {len(test_obs_list)} targets (for testing)")
    print("="*60)

def main():
    """Parse command line arguments and generate observing blocks."""
    parser = argparse.ArgumentParser(
        description=f'Generate KPF Observing Blocks for November, December, or January ({YEAR}B semester)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --month nov                    # Use default strategy (version1)
  %(prog)s --month dec
  %(prog)s --strategy version1 --month jan
  %(prog)s -s version1 -m nov -t 5        # With 5 test targets
        """
    )
    
    parser.add_argument(
        '-m', '--month',
        type=str,
        required=True,
        choices=['nov', 'dec', 'jan'],
        help='Month for observations: nov, dec, or jan'
    )
    
    parser.add_argument(
        '-s', '--strategy',
        type=str,
        default='version1',
        choices=['version1'],
        help='Observing strategy version (default: version1)'
    )
    
    parser.add_argument(
        '-t', '--test-targets',
        type=int,
        default=2,
        help='Number of targets to include in test file (default: 2)'
    )
    
    args = parser.parse_args()
    
    generate_obs(args.month, args.strategy, args.test_targets)

if __name__ == "__main__":
    main()
