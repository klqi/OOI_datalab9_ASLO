from erddapy import ERDDAP
import numpy as np
import pandas as pd
import config

## helper function to start ERDDAP connection
def set_connection():
    server = "https://erddap.dataexplorer.oceanobservatories.org/erddap/"
    e = ERDDAP(
        server=server,
        protocol="tabledap",
        response="csv",
    )
    return e

## helper functions
# read in OOI data by erddapy
def read_ooi_data(e, id, start_time, end_time, vars, station):
  ## debugging
  print(id)
  print(vars)
  url_path = e.get_download_url(
      dataset_id = id,
      constraints = {
        "time>=": start_time,
        "time<=": end_time,
      },
      variables = vars
  )
  df = pd.read_csv(url_path, parse_dates=True, skiprows=[1])
  df['station'] = station
  return df

# helper function to read and clean OOI Data
def clean_ooi_data(e, station, chl_var, chl_id, clean_cols_chl,
                   nitrate_id, nitrate_var, clean_cols_nitrate,
                   light_id, light_var, clean_cols_light,
                   start_time, end_time):
    # read in chl data 
    chl_df = read_ooi_data(e, chl_id, start_time, end_time, chl_var, station)
    chl_df.columns = clean_cols_chl
    # grab clean and store in nitrate nitrate_dfs
    nitrate_df=read_ooi_data(e, nitrate_id, start_time, end_time, nitrate_var, station)
    nitrate_df.columns = clean_cols_nitrate
    # grab all light and clean and store
    light_df=read_ooi_data(e, light_id, start_time, end_time, light_var, station)
    light_df.columns = clean_cols_light
    
    return chl_df, nitrate_df, light_df

# remove outliers by std, default 3 (thanks gemini)
def remove_outliers_std(df, column, threshold=3):
  """
  Removes outliers from a pandas DataFrame column based on the standard deviation.

  Args:
    df: The pandas DataFrame.
    column: The name of the column to remove outliers from.
    threshold: The number of standard deviations from the mean to consider an outlier.

  Returns:
    A new DataFrame with outliers removed.
  """
  mean = df[column].mean()
  std = df[column].std()
  # instead of removing outliers, set to nan if there are any
  if not df.loc[(df[column] <= mean - threshold * std) | (df[column] >= mean + threshold * std)].empty:
    df.loc[(df[column] <= mean - threshold * std) | (df[column] >= mean + threshold * std), column] = np.nan
  return df

# resample to daily resolution
def summarize_daily(df, station):
    df['time'] = pd.DatetimeIndex(df['time']).tz_convert('UTC')
    daily_df = df.set_index('time').resample('1D').asfreq()
    daily_df['station'] = station
    return(daily_df)

# function to set up ERDDAP connection and read in data
def load_data():
    # set erddap connection
    e = set_connection()
    # store dfs in empty lists
    chl_dfs = []
    nitrate_dfs = []
    light_dfs = []
    for station, chl_var, chl_id, nitrate_id, light_id, in zip(config.stations, config.chl_vars, config.chl_ids, config.nitrate_ids, config.light_ids):
        # get formatted data
        chl_df, nitrate_df, light_df = clean_ooi_data(e, station, chl_var, chl_id, config.clean_cols_chl,
                                                    nitrate_id, config.nitrate_vars, config.clean_cols_nitrate, 
                                                    light_id, config.light_vars, config.clean_cols_light, 
                                                    config.start_time, config.end_time)
        # clean by removing outiers
        clean_df = remove_outliers_std(chl_df, 'chl')
        # also clean temp
        clean_chl = summarize_daily(remove_outliers_std(clean_df, 'sst', 3), station)
        clean_no3 = summarize_daily(remove_outliers_std(nitrate_df, 'no3', 3), station)
        clean_light = summarize_daily(remove_outliers_std(light_df, 'light', 3), station)
        # store in lists
        chl_dfs.append(clean_chl)
        nitrate_dfs.append(clean_no3)
        light_dfs.append(clean_light)
    # concatenate all dfs
    all_chl = pd.concat(chl_dfs).reset_index()
    all_no3 = pd.concat(nitrate_dfs).reset_index()
    all_light = pd.concat(light_dfs).reset_index()
    return all_chl, all_no3, all_light