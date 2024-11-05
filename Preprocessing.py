import pandas as pd
from datetime import timedelta
import glob
import pyodbc

def add_trip_ids(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # Calculate time difference between consecutive rows
    time_diff = df['datetime'].diff()
    
    # New trip starts when time difference > 30 minutes (and for first record)
    new_trip = (time_diff > timedelta(minutes=30)) | (time_diff.isna())
    
    
    df['trip_id'] = new_trip.cumsum()
    
    return df


def process_taxi_file(file_path):

    df = pd.read_csv(file_path, 
                     names=['taxi_id', 'datetime', 'longitude', 'latitude'])
    
    initial_rows = len(df)
    df = df.drop_duplicates()
    dropped_rows = initial_rows - len(df)
    
    if dropped_rows > 0:
        print(f"Removed {dropped_rows} duplicate rows from {file_path}")
        
 
    df_with_trips = add_trip_ids(df)
    
    return df_with_trips

def add_trip_ids(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)
    
    # Calculate time difference between consecutive rows
    time_diff = df['datetime'].diff()
    
    # New trip starts when time difference > 30 minutes (and for first record)
    new_trip = (time_diff > timedelta(minutes=30)) | (time_diff.isna())
    
    
    df['trip_id'] = new_trip.cumsum()
    
    return df


result_df = pd.DataFrame()
# Change the file path here
#for file_path in glob.glob('C:\\Users\\TinBu\\OneDrive\\Desktop\\TCSS 565\\SpatialDBProject\\User_Trajectories\\*.txt'):
for file_path in glob.glob('C:\\Users\\TinBu\\OneDrive\\Desktop\\TCSS 565\\SpatialDBProject\\Trajectory_Dataset\\*.txt'):
    df = process_taxi_file(file_path)
    result_df = pd.concat([result_df, df], ignore_index=True)

result_df.to_csv('processed_dataset.csv', index=False)

result_df.dtypes
