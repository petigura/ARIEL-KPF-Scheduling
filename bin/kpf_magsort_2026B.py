#!/usr/bin/env python3
"""
Create two groups of KPF targets, sorted by magnitude (highest to lowest)
Each group covers the same interval of time.
Designed to split up 2026B semester targets into two equally long groups
"""

import pandas as pd
import numpy as np
from ariel_kpf.paths import TARGETS_DIR, get_latest_kpf_targets_file

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(get_latest_kpf_targets_file())

def monthSort(RA):
    """
    Sorts RA values into their respective observation month.

    Parameters
    ----------
    RA : Right Ascension in J2000 epoch of a target (Series)

    Returns
    -------
    months : The 2-month span corresponding to each RA value (Series)
    """

    if ((RA >= 120.) & (RA < 180.)):

        return 'feb/mar'
    elif((RA >= 180.) & (RA < 240.)):

        return 'apr/may'
    elif ((RA >= 240.) & (RA < 300.)):

        return 'jun/jul'
    else:
        return 'N/A'



def magSort():
    """
    Create two groups of KPF targets, sorted by magnitude,
    that cover the same interval of time. Each group is 
    additionally split into months. The months take up the same
    amount of time. 
    """
    print('Extracting latest KPF target list...')
    master_df = pd.read_csv(get_latest_kpf_targets_file()) #Pull latest KPF targets datasheet
    print('Sorting targets into observation months...')


    overhead = 180 #edit this number for a particular overhead. 3 minutes as per J. Lubin 1/19/26
    #Sorting by RA into monthlong bins
    sem_df = master_df[(master_df['ra'] >= 120.) & (master_df['ra'] <= 300.)] #Sifting master df to only include targets within our desired RA range
    sem_df.loc[:, 't_sec_kpf'] = sem_df['t_sec_kpf'] + overhead #adding overhead offset
    sem_df.loc[:, 't_sec_kpf'] = sem_df['t_sec_kpf'] * 4 #four observations in a semester is our chosen cadence
    sem_df.sort_values(by = 'v_mag', ascending = True, inplace = True) #Sorting to have smallest magnitude (i.e. brightest) stars first
    sem_df.reset_index(inplace = True) #resetting index for clarity

    sem_df['month'] = sem_df['ra'].apply(monthSort) #generating new column of month strings, using monthSort()
    counts = sem_df['month'].value_counts() #counting up number of targets per month

    #new month-specific dataframes
    febMar_df = sem_df[sem_df['month'] == 'feb/mar']
    aprMay_df = sem_df[sem_df['month'] == 'apr/may']
    junJul_df = sem_df[sem_df['month'] == 'jun/jul'] 

    #calculating total time
    febMar_t = febMar_df['t_sec_kpf'].sum()
    aprMay_t = aprMay_df['t_sec_kpf'].sum()
    junJul_t = junJul_df['t_sec_kpf'].sum()
    tot_t = sem_df['t_sec_kpf'].sum()

    def cut_index_by_half(df):
        """
        Function to automate halfway point search to ensure each split sums to the same time.

        Parameters:
        ----------
        df - DataFrame of semester/month set targets containing a column labeled 't_sec_kpf',
             which is the exposure time required for each target.

        Returns:
        ----------
        pos - index position within the dataframe that splits df in half such that the two halves
              contain targets of equal length. NOT necessarily same number of targets.

        """
        half = df['t_sec_kpf'].sum() / 2.0 #find halfway time
        cuml = df['t_sec_kpf'].cumsum() # take cumulative sum of time, as a series
        pos = cuml.searchsorted(half, side='left') #using searchsorted() to find where in the df the halfway time should be

        # guard ends to avoid errors thrown
        if pos == 0:
            return 0
        if pos >= len(df):
            return len(df) - 1

        left_sum = cuml.iloc[pos-1] #Identify sum leftward of center
        right_sum = cuml.iloc[pos] # "              " rightward of center
        return (pos-1) if (half - left_sum) <= (right_sum - half) else pos #return whichever position split gives the smallest difference

    #compute cut positions for each df
    tot_cut_idx = cut_index_by_half(sem_df)
    febMar_cut_idx = cut_index_by_half(febMar_df) if len(febMar_df) else None #Safeguard against empty dfs
    aprMay_cut_idx = cut_index_by_half(aprMay_df) if len(aprMay_df) else None
    junJul_cut_idx = cut_index_by_half(junJul_df) if len(junJul_df) else None

    #Split by index (no double-count)
    sem_up_df = sem_df.iloc[:tot_cut_idx+1].copy()
    sem_lo_df = sem_df.iloc[tot_cut_idx+1:].copy()

    febMar_up_df = febMar_df.iloc[:febMar_cut_idx+1].copy() if febMar_cut_idx is not None else febMar_df.copy()
    febMar_lo_df = febMar_df.iloc[febMar_cut_idx+1:].copy() if febMar_cut_idx is not None else febMar_df.iloc[0:0].copy()

    aprMay_up_df = aprMay_df.iloc[:aprMay_cut_idx+1].copy() if aprMay_cut_idx is not None else aprMay_df.copy()
    aprMay_lo_df = aprMay_df.iloc[aprMay_cut_idx+1:].copy() if aprMay_cut_idx is not None else aprMay_df.iloc[0:0].copy()

    junJul_up_df = junJul_df.iloc[:junJul_cut_idx+1].copy() if junJul_cut_idx is not None else junJul_df.copy()
    junJul_lo_df = junJul_df.iloc[junJul_cut_idx+1:].copy() if junJul_cut_idx is not None else junJul_df.iloc[0:0].copy()

    #Defining cutoff magnitudes for V and TESS
    tot_cut_vmag = sem_df['v_mag'].iloc[tot_cut_idx]
    print(tot_cut_vmag)
    tot_cut_tmag = sem_df['tess_mag'].iloc[tot_cut_idx]
    febMar_cut_vmag = febMar_df['v_mag'].iloc[febMar_cut_idx]
    febMar_cut_tmag = febMar_df['tess_mag'].iloc[febMar_cut_idx]
    aprMay_cut_vmag = aprMay_df['v_mag'].iloc[aprMay_cut_idx]
    aprMay_cut_tmag = aprMay_df['tess_mag'].iloc[aprMay_cut_idx]
    junJul_cut_vmag = junJul_df['v_mag'].iloc[junJul_cut_idx]
    junJul_cut_tmag = junJul_df['tess_mag'].iloc[junJul_cut_idx]

    #Printing results
    print('='*80)
    print('Total KPF Targets:', len(sem_df['ra']))
    print('Total Time:', np.round(tot_t / 3600, 2))
    print('Cutoff V magnitude:', np.round(tot_cut_vmag, 2))
    print('Cutoff TESS magnitude:', np.round(tot_cut_tmag, 2))
    print('-'*80)
    print('February/March:', counts['feb/mar'], 'targets')
    print('Minimum RA: 120 ~ Maximum RA: 180')
    print('Total Time:', np.round(febMar_t/3600, 2), 'hours')
    print('Cutoff V magnitude:', np.round(febMar_cut_vmag, 2))
    print('Cutoff TESS magnitude:', np.round(febMar_cut_tmag,2))
    print('-'*80)
    print('April/May:', counts['apr/may'], 'targets')
    print('Minimum RA: 180 ~ Maximum RA: 240')
    print('Total Time:', np.round(aprMay_t/3600, 2), 'hours')
    print('Cutoff V magnitude:', np.round(aprMay_cut_vmag, 3))
    print('Cutoff TESS magnitude:', np.round(aprMay_cut_tmag, 3))
    print('-'*80)
    print('Jun/July:', counts['jun/jul'], 'targets')
    print('Minimum RA: 240  Maximum RA: 300')
    print('Total Time:', np.round(junJul_t/3600, 2), 'hours')
    print('Cutoff V magnitude:', np.round(junJul_cut_vmag, 3))
    print('Cutoff TESS magnitude:', np.round(junJul_cut_tmag, 3))
    print('='*80)

    #Defining new split dfs
    sem_up_df = sem_df[sem_df['v_mag'] <= tot_cut_vmag] #Take upper half with smaller magnitude (brighter stars) from whole semester
    sem_lo_df = sem_df[sem_df['v_mag'] > tot_cut_vmag]
    febMar_up_df = febMar_df[febMar_df['v_mag'] <= febMar_cut_vmag] #Take upper half with smaller magnitude (brighter stars) from February + March
    febMar_lo_df = febMar_df[febMar_df['v_mag'] > febMar_cut_vmag]
    aprMay_up_df = aprMay_df[aprMay_df['v_mag'] <= aprMay_cut_vmag] #"          "
    aprMay_lo_df = aprMay_df[aprMay_df['v_mag'] > aprMay_cut_vmag]
    junJul_up_df = junJul_df[junJul_df['v_mag'] <= junJul_cut_vmag] #"          "
    junJul_lo_df = junJul_df[junJul_df['v_mag'] > junJul_cut_vmag] 

    #Printing binned statistics
    print(f'2026B Semester KPF Targets, Split by Magnitude ({len(sem_df["month"])} targets)')
    print(f'+{overhead} seconds overhead')
    print('='*80)
    print(f'Full Semester, 2026B ({len(sem_up_df["v_mag"])} brighter targets):')
    print('V magnitude range:', np.round(np.max(sem_up_df['v_mag']),3), 'to', np.round(np.min(sem_up_df['v_mag']), 3))
    print('Total Observing Time:', np.round(np.sum(sem_up_df['t_sec_kpf']) / 3600, 3), 'hours')
    print(f'Full Semester, 2027B ({len(sem_lo_df["v_mag"])} dimmer targets)')
    print('V magnitude range:', np.round(np.max(sem_lo_df["v_mag"]),3), 'to', np.round(np.min(sem_lo_df['v_mag']), 3))
    print('Total Observing Time:', np.round(np.sum(sem_lo_df['t_sec_kpf']) / 3600, 3), 'hours')
    print('Total Difference:', np.round((np.sum(sem_up_df['t_sec_kpf']) - np.sum(sem_lo_df['t_sec_kpf']))/3600, 3), "hours")
    print('-'*80)
    print(f'February/March 2026 ({len(febMar_up_df["v_mag"])} low magnitude targets)')
    print('V magnitude range:', np.round(np.max(febMar_up_df['v_mag']),3), 'to', np.round(np.min(febMar_up_df['v_mag']), 3))
    print('Total Observing Time:', np.round(np.sum(febMar_up_df['t_sec_kpf']) / 3600, 3), 'hours')
    print(f'February/March 2027 ({len(febMar_lo_df["v_mag"])} high magnitude targets)')
    print('V magnitude range:', np.round(np.max(febMar_lo_df['v_mag']),3), 'to', np.round(np.min(febMar_lo_df['v_mag']),3))
    print('Total Observing Time:', np.round(np.sum(febMar_lo_df['t_sec_kpf']) / 3600, 3), 'hours')
    print('Total Difference:', np.round((np.sum(febMar_up_df['t_sec_kpf']) - np.sum(febMar_lo_df['t_sec_kpf']))/3600, 3), "hours")
    print('-'*80)
    print(f'April/May 2026 ({len(aprMay_up_df["v_mag"])} low magnitude targets)')
    print('V magnitude range:', np.round(np.max(aprMay_up_df['v_mag']),3), 'to', np.round(np.min(aprMay_up_df['v_mag']),3))
    print('Total Observing Time:', np.round(np.sum(aprMay_up_df['t_sec_kpf']) / 3600, 3), 'hours')
    print(f'April/May 2027 ({len(aprMay_lo_df["v_mag"])} high magnitude targets)')
    print('V magnitude range:', np.round(np.max(aprMay_lo_df['v_mag']),3), 'to', np.round(np.min(aprMay_lo_df['v_mag']),3))
    print('Total Observing Time:', np.round(np.sum(aprMay_lo_df['t_sec_kpf']) / 3600, 3), 'hours')
    print('Total Difference:', np.round((np.sum(aprMay_up_df['t_sec_kpf']) - np.sum(aprMay_lo_df['t_sec_kpf']))/3600, 3), "hours")
    print('-'*80)
    print(f'June/July 2026 ({len(junJul_up_df["v_mag"])} low magnitude targets)')
    print('V magnitude range:', np.round(np.max(junJul_up_df['v_mag']),3), 'to', np.round(np.min(junJul_up_df['v_mag']),3))
    print('Total Observing Time:', np.round(np.sum(junJul_up_df['t_sec_kpf']) / 3600, 3), 'hours')
    print(f'June/July 2027 ({len(junJul_lo_df["v_mag"])} high magnitude targets)')
    print('V magnitude range:', np.round(np.max(junJul_lo_df['v_mag']),3), 'to', np.round(np.min(junJul_lo_df['v_mag']),3))
    print('Total Observing Time:', np.round(np.sum(junJul_lo_df['t_sec_kpf']) / 3600, 3), 'hours')
    print('Total Difference:', np.round((np.sum(junJul_up_df['t_sec_kpf']) - np.sum(junJul_lo_df['t_sec_kpf']))/3600, 3), "hours")
    print('-'*80)




if __name__ == "__main__":
    magSort()














    