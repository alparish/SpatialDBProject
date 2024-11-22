import pandas as pd
from datetime import timedelta
import glob
import pyodbc
from math import radians, sin, cos, sqrt, atan2
from shapely.geometry import Point

def haversine_distance(point1, point2):
    R = 6371  # Earth's radius in kilometers

    lat1, lon1 = radians(point1.y), radians(point1.x)
    lat2, lon2 = radians(point2.y), radians(point2.x)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c
    
    return distance

def calculate_speed(row1, row2):
    point1 = Point(row1['longitude'], row1['latitude'])
    point2 = Point(row2['longitude'], row2['latitude'])
    
    # Calculate distance in kilometers
    distance = haversine_distance(point1, point2)
    
    # Calculate time difference in hours
    time_diff = (row2['datetime'] - row1['datetime']).total_seconds() / 3600
    
    # Calculate speed in km/h
    if time_diff > 0:
        speed = distance / time_diff
    else:
        speed = float('inf')
    
    return speed

def process_taxi_file(file_path, max_speed_kmh=120, min_points=2, max_points=15):
    # Read the CSV file
    df = pd.read_csv(file_path, 
                     names=['taxi_id', 'datetime', 'longitude', 'latitude'])
    
    # Remove duplicate rows
    initial_rows = len(df)
    df = df.drop_duplicates()
    print(f"Removed {initial_rows - len(df)} duplicate rows")
    
    # Convert datetime
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Sort by datetime
    df = df.sort_values('datetime').reset_index(drop=True)
    
    valid_indices = []
    trip_ids = []
    current_trip = []
    current_trip_id = 0
    
    i = 0
    while i < len(df):
        if not current_trip:  # If starting a new trip
            current_trip.append(i)
            i += 1
            continue
        
        # Calculate speed from previous point
        speed = calculate_speed(
            df.iloc[current_trip[-1]], 
            df.iloc[i]
        )
        
        # Check if time gap is too large (30 minutes)
        time_gap = (df.iloc[i]['datetime'] - 
                   df.iloc[current_trip[-1]]['datetime']).total_seconds() / 60
        
        if time_gap > 30:  # End current trip and start new one
            if len(current_trip) >= min_points:
                valid_indices.extend(current_trip)
                trip_ids.extend([current_trip_id] * len(current_trip))
                current_trip_id += 1
            current_trip = [i]
            
        elif len(current_trip) >= max_points:  # Trip reached max length
            valid_indices.extend(current_trip)
            trip_ids.extend([current_trip_id] * len(current_trip))
            current_trip_id += 1
            current_trip = [i]
            
        elif speed > max_speed_kmh:  # Skip this point if speed is too high
            i += 1
            continue
            
        else:  # Add point to current trip
            current_trip.append(i)
            
        i += 1
    
    if len(current_trip) >= min_points:
        valid_indices.extend(current_trip)
        trip_ids.extend([current_trip_id] * len(current_trip))
    
    # Create filtered dataframe
    if valid_indices:
        df_filtered = df.iloc[valid_indices].copy()
        df_filtered['trip_id'] = trip_ids
        
        return df_filtered
    else:
        return pd.DataFrame() 

def process_all_files(directory_path, max_speed_kmh=120):
    result_df = pd.DataFrame()
    file_pattern = f"{directory_path}/*.txt"
    
    total_files = 0
    total_initial_rows = 0
    total_final_rows = 0
    total_trips = 0
    
    for file_path in glob.glob(file_pattern):
        df_initial = pd.read_csv(file_path, 
                               names=['taxi_id', 'datetime', 'longitude', 'latitude'])
        total_initial_rows += len(df_initial)
        
        df = process_taxi_file(file_path, max_speed_kmh=max_speed_kmh)
        if not df.empty:
            total_final_rows += len(df)
            total_trips += df['trip_id'].nunique()
            result_df = pd.concat([result_df, df], ignore_index=True)
        
        total_files += 1
        print(f"Processed {file_path}")
    
    print("\nProcessing Summary:")
    print(f"Total files processed: {total_files}")
    print(f"Total initial rows: {total_initial_rows}")
    print(f"Total final rows: {total_final_rows}")
    print(f"Total trips: {total_trips}")
    print(f"Points removed: {total_initial_rows - total_final_rows}")
    print(f"Average points per trip: {total_final_rows / total_trips:.2f}")
    
    return result_df

directory_path = "C:\\Users\\TinBu\\OneDrive\\Desktop\\TCSS 565\\SpatialDBProject\\Trajectory_Dataset\\"
result_df = process_all_files(directory_path, max_speed_kmh=120)

result_df.to_csv('processed_dataset.csv', index=False)
