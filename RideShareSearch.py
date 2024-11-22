
import PySimpleGUI as sg # type: ignore
import pandas as pd
import argparse
import os
import random
import numpy as np
import gmplot
import webbrowser
import pyodbc
import csv
import itertools
from geopy.distance import geodesic
from datetime import datetime
from itertools import combinations
from datetime import timedelta

def read_file(file_path):
    user_file = pd.read_csv(file_path, header=None)
    user_file.rename(columns={0: 'latitude', 1: 'longitude', 2: 'timestamp'}, inplace=True)
    user_file['id'] = int(0)
    user_file['timestamp'] = pd.to_datetime(user_file['timestamp'])
    return user_file

def enter_file():
    layout_file = [[sg.Text("Enter the directory path to your file.")],
                   [sg.Text('file', size=(12,1)), sg.In(k='-File-', size=(10,1))],
                   [sg.Button('Enter', key='Enter'), sg.Button('Cancel', key='Cancel')]]
    file_window = sg.Window('Enter File', layout_file, font='20')
    while True:
        event, values = file_window.read()
        if event =='Enter':
            # Need to check if it is a valid path and file exists, otherwise throw a popup error
            user_file = pd.read_csv(values['-File-'], header=None)
            user_file.rename(columns={0: 'latitude', 1: 'longitude', 2: 'timestamp'}, inplace=True)
            user_file['id'] = int(0)
            user_file['timestamp'] = pd.to_datetime(user_file['timestamp'])
            file_window.close()
            return user_file 
        elif event == 'Cancel':
            # Need to also break from the app
            file_window.close()
            return None
        elif event == sg.WIN_CLOSED:
            file_window.close()
            return None


def enter_points():
    layout = [[sg.Text("Enter a latitude value in (39.819782, 39.983785)")],
              [sg.Text("and longitude value in (116.255068, 116.533949)")],
              [sg.Text('latitude', size=(12,1)), sg.In(k='-Lat-', size=(10,1))],
              [sg.Text('longitude', size=(12,1)), sg.In(k='-Long-', size=(10,1))],
              [sg.Text("Enter a date and time")],
              [sg.Text('YYYY-MM-DD', size=(12,1)), sg.In(k='-Date-', size=(10,1))],
              [sg.Text('HH:MM:SS', size=(12,1)), sg.In(k='-Time-', size=(10,1))],
              [sg.Button('Enter Another Point', key='Next'), sg.Button('Submit Trajectory', key='Submit')]]
    
    window = sg.Window('Enter your Trajectory GPS points', layout, font='20')
    # Event Loop to process "events" and get the "values" of the inputs
    
    trajectory = pd.DataFrame(columns=['id', 'latitude', 'longitude', 'timestamp'])
    id = int(0)
    while True:
        event, values = window.read()
        
        if event == 'Next':
            print('The point entered is', values['-Lat-'], values['-Long-'], values['-Date-'], values['-Time-'])
            try:
                lat = float(values['-Lat-'])
                long = float(values['-Long-'])
                date = values['-Date-']
                time = values['-Time-']
                time_stamp = date + ' ' + time
                if lat < 39.819783 or lat > 39.983785 or long < 116.255068 or long > 116.533949:
                    print("Sorry, that point is outside the service area. Please enter a new point.")
                    sg.popup_error("Sorry, that point is outside the service area. Please enter a new point.")
                    window['-Lat-'].update(' ')
                    window['-Long-'].update(' ')
                    window['-Time-'].update(' ')
                    window['-Date-'].update(' ')
                else:
                    trajectory.loc[len(trajectory)] = [id, lat, long, time_stamp]
                    window['-Lat-'].update(' ')
                    window['-Long-'].update(' ')
            except ValueError:
                print("Invalid Entry. Please enter a number.")
                sg.popup_error("Invalid Entry. Please enter a number.")
        elif event == 'Submit':
            print('The point entered is', values['-Lat-'], values['-Long-'], values['-Date-'], values['-Time-'])
            try:
                lat = float(values['-Lat-'])
                long = float(values['-Long-'])
                date = values['-Date-']
                time = values['-Time-']
                time_stamp = date + ' ' + time
                if lat < 39.819783 or lat > 39.983785 or long < 116.255068 or long > 116.533949:
                    print("Sorry, that point is outside the service area.")
                    sg.popup_error("Sorry, that point is outside the service area.")
                    window['-Lat-'].update(' ')
                    window['-Long-'].update(' ')
                    window['-Time-'].update(' ')
                    window['-Date-'].update(' ')
                else:
                    trajectory.loc[len(trajectory)] = [id, lat, long, time_stamp]
                    window['-Lat-'].update(' ')
                    window['-Long-'].update(' ')
            except ValueError:
                print("Invalid Entry.")
                sg.popup_error("Invalid Entry.")
            window.close()
            return trajectory
        elif event == sg.WIN_CLOSED:
            window.close()
            return None

def get_trajectory():
    layout_welcome = [[sg.Text("Welcome to your Ride Share Tool")],
                  [sg.Text("Do you want to upload a file with your trajectory points")],
                  [sg.Text("or enter indivual latitude and longitude points here?")],
                  [sg.Button('Upload a file', key='File'), sg.Button('Enter individual points', key = 'Points')]]
    welcome_window = sg.Window('Ride Share', layout_welcome, font='20')
    
    while True:
        event, values = welcome_window.read()
        if event == 'File':
            # read a file with trajectory
            welcome_window.close()
            user_traj = enter_file()
            return user_traj
        elif event == 'Points':
            # open the point window
            welcome_window.close()
            user_traj = enter_points()
            return user_traj
        elif event == sg.WIN_CLOSED:
            # close window and close app, no trajectories means no matches
            return None

def get_random_trajectory(numtraj):
    server = 'localhost'
    database = 'master'
    
    conn_str = (
        'Driver={ODBC Driver 18 for SQL Server};'
        f'Server={server};'
        f'Database={database};'
        'Trusted_Connection=yes;'
        'TrustServerCertificate=yes;'
        )
    
    # Create connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected to the database, selecting a random trajectory")


    traj_id = int(random.randint(1, numtraj))
    string = ''


    select_query = """
        SELECT latitude, longitude, datetime, id FROM taxi_trips
        WHERE id = ? 
        """
    
    try:
        cursor.execute(
                    select_query,
                    traj_id
                )
    except Exception as e:
        print(f"Error selecting")
        raise

    result = cursor.fetchall()

    n = len(result)

    trajectory = pd.DataFrame(columns=['id', 'timestamp', 'latitude', 'longitude'])
    for i in range(0,n):
        time_stamp = result[i][2]
        lat = result[i][0]
        long = result[i][1]
        trajectory.loc[len(trajectory)] = [traj_id, time_stamp, lat, long]


    conn.commit()
    cursor.close()
    conn.close()

    return trajectory
            
def get_parameters():
    layout_param = [
        [sg.Text("How important is reducing the walking distance from your starting location to you?\n" + 
                "A low importance will allow for close matches that start further away from your starting point.\n" +
                "Higher importance will rank matches that start closer to your starting point higher.")],
        [sg.Slider(range=(0,10), orientation='h', default_value = 0, tick_interval=1, key='DIST' )],
        [sg.Text("How important is the start time of your trip?\n" +
                 "A low importance will allow for close matches that start at other times in the day.\n" +
                 "A higher importance will rank matches that start closer to your starting time higher\n" +
                 "(even if the match is not ideal).")],
        [sg.Slider(range=(0,10), default_value = 0, orientation='h', tick_interval = 1, key='TIME')],
        [sg.Text("How important is the order in which you visit the stops?\n" + 
                 "A low importance will allow for matches with rides that visit the same (or similar) stops in a different order.\n" +
                 "A higher importance will rank matches higher that visit stops in the same order.")],
        [sg.Slider(range=(0,10), default_value=0, tick_interval = 1, orientation = 'h', key='ORDER')],
        [sg.Button('Go', key='Go'), sg.Button('Cancel', key='Cancel')]]

    
    param_window = sg.Window('Establish Parameters', layout_param, font='20')
    
    while True:
        event, values = param_window.read()
        
        if event == 'Go':
            time_val = values['TIME']
            dist_val = values['DIST']
            order_val = values['ORDER']

            total = time_val + dist_val + order_val

            param_window.close()

            return time_val, dist_val, order_val
        elif event == 'Cancel':
            param_window.close()
            return None
        elif event == sg.WIN_CLOSED:
            param_window.close()
            return None
        
def find_intersections(usertraj):
    server = 'localhost'
    database = 'master'
    
    conn_str = (
        'Driver={ODBC Driver 18 for SQL Server};'
        f'Server={server};'
        f'Database={database};'
        'Trusted_Connection=yes;'
        'TrustServerCertificate=yes;'
        )
    
    # Create connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected to the database, finding intersections")

    #df = pd.read_sql('SELECT t.id, t.seq, t.longitude, t.latitude FROM taxi_trips as t', conn)

    traj_id = int(usertraj['id'][0])
    string = ''

    for index, row in usertraj.iterrows():
        if string == '':
            string = 'LINESTRING(' + str(row['longitude']).strip()  + ' ' + str(row['latitude']).strip()
        else:
            string = string + ',' + str(row['longitude']).strip() + ' ' + str(row['latitude']).strip()
    string = string + ')'


    insert_query = """
        INSERT INTO Trajectories
            (id, Shape, ShapeGeography)
        VALUES 
            (?, ?, geography::STLineFromText(?, 4326).MakeValid())
        """
    

    try:
        cursor.execute(
                    insert_query,
                    traj_id,
                    string,
                    string
                )
    except Exception as e:
        print(f"Error inserting")
        raise

    sql_intersect = """
        SELECT TOP 20 T2.Id, Area = T1.ShapeGeography.STBuffer(20).STIntersection(T2.ShapeGeography.STBuffer(20)).STArea()
        FROM Trajectories T1 JOIN Trajectories T2
        ON T1.ShapeGeography.STBuffer(20).STIntersects(T2.ShapeGeography.STBuffer(20))=1 AND T1.Id = ? AND T2.Id != T1.Id
        ORDER BY Area DESC;
        """

    try:
        cursor.execute(sql_intersect, traj_id)
        result = cursor.fetchall()
    except Exception as e:
        print(f"Error {e}")
        raise


    # What about when a random trajectory is selected, should be removing id? no.
    sql_remove = f'DELETE FROM Trajectories WHERE id={traj_id};'
    cursor.execute(sql_remove)
    conn.commit()
    cursor.close()
    conn.close()

    return result


# DTW Algorithm Implementation that cuts off if every
# value in the dynamic array is bigger than the max_val
def quick_dtw(trip1, trip2, max_val):
    n, m = len(trip1), len(trip2)
    max_val = max_val * max_val * max(n, m)

    # Initialize the DTW matrix with infinity
    dtw_matrix = np.zeros((n + 1, m + 1))
    dtw_matrix[0, 1:] = float('inf')
    dtw_matrix[1:, 0] = float('inf')

    # Fill the DTW matrix
    for i in range(1, n + 1):
        has_small_val = False
        for j in range(1, m + 1):
            # Calculate distance between points
            cost = geodesic(trip1[i - 1][:2], trip2[j - 1][:2]).miles
            dtw_matrix[i, j] = cost**2 + min(dtw_matrix[i - 1, j],
                                          dtw_matrix[i, j - 1],   
                                          dtw_matrix[i - 1, j - 1])
            if dtw_matrix[i, j] < max_val:
                has_small_val = True
        
        # If every entry is already too large, quit and return infinity
        if has_small_val == False:
            return float('inf')
    # Normalize the DTW distance
    dtw_distance = dtw_matrix[n, m]
    normalized_dtw = np.sqrt(dtw_distance / max(n, m))

    # Return the normalized DTW distance
    return normalized_dtw

def reorder_rows(array, permutation):
    return array[permutation]

# The following implementation comes from geeksforgeeks.org
def mergeSort(arr, n):
    # A temp_arr is created to store sorted array in merge function
    temp_arr = [0]*n
    return _mergeSort(arr, temp_arr, 0, n-1)

# This function uses MergeSort to count inversions
def _mergeSort(arr, temp_arr, left, right):
    inv_count = 0

    if left < right:
        mid = (left + right) // 2

        inv_count += _mergeSort(arr, temp_arr, left, mid)

        inv_count += _mergeSort(arr, temp_arr, mid + 1, right)

        inv_count += merge(arr, temp_arr, left, mid, right)
    
    return inv_count

def merge(arr, temp_arr, left, mid, right):
    # Starting index of left subarray
    i = left
    # Starting index of right subarray
    j = mid + 1
    # Starting index of to be sorted subarray
    k = left
    inv_count = 0

    while i <= mid and j <= right:
        # No inversions if arr[i] <= arr[j]
        if arr[i] <= arr[j]:
            temp_arr[k] = arr[i]
            k += 1
            i += 1
        else:
            # inversions occur
            temp_arr[k] = arr[j]
            inv_count += (mid - i + 1)
            k += 1
            j += 1
    
    while i <= mid:
        temp_arr[k] = arr[i]
        k += 1
        i += 1
    
    while j <= right:
        temp_arr[k] = arr[j]
        k += 1
        j += 1
    
    for loop_var in range(left, right + 1):
        arr[loop_var] = temp_arr[loop_var]

    return inv_count

def calculate_single_inversion_distance(array):
    sorted_array_for_counting = array.copy()
    count = mergeSort(sorted_array_for_counting, len(array))
    return count

# usertraj is the original user trajectory, 
# result is a collection of trajectories running close to the user trajectory
# the time, distance, and order weight are parameters established by the user    
def weighted_dtw_on_intersections(usertraj, result, time_weight, distance_weight, order_weight):
    server = 'localhost'
    database = 'master'
    
    user_info = usertraj.loc[:, ['latitude', 'longitude', 'timestamp', 'id']]
    permuted_traj = user_info.copy()
    all_traj = user_info.copy()
    user_array = user_info.to_numpy()
    user_start_time = usertraj.iloc[0]['timestamp']
    dtw_min = dtw_min = float('inf')

    conn_str = (
        'Driver={ODBC Driver 18 for SQL Server};'
        f'Server={server};'
        f'Database={database};'
        'Trusted_Connection=yes;'
        'TrustServerCertificate=yes;'
    )
    
    # Create connection
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Connected to the database inside weighted dtw")

    # for every permutation of the user's points,
    n = len(usertraj)
    seq = list(itertools.chain(range(0, n)))
    permutations = list(itertools.islice(itertools.permutations(seq),0, n*(n-1), n-1))
    permutations_as_array = np.array(permutations)
    min_id = 0
    for row in permutations_as_array:
        perm_array = row
        permuted_traj = user_info.iloc[perm_array]

        user_lat = permuted_traj ['latitude']
        user_long = permuted_traj['longitude']

        # Get the starting point's coordinates
        user_start_lat = user_lat.iloc[0]
        user_start_long = user_long.iloc[0]

        for row in result:
            traj_id = row[0]

            sql_select = """
                SELECT latitude, longitude, datetime, id
                FROM taxi_trips
                WHERE id = ?
                ORDER BY seq ASC;
            """
            cursor.execute(sql_select, traj_id)
            traj_match = cursor.fetchall()

            #calculate the scale factors
            match_start_lat, match_start_long, match_start_time, _ = traj_match[0]
            match_start_time = pd.to_datetime(match_start_time)
            start_distance = geodesic((user_start_lat, user_start_long), (match_start_lat, match_start_long)).miles
            time_diff = float(abs((user_start_time - match_start_time).total_seconds() / 3600))
            distance_scale = 1 + start_distance * distance_weight
            time_scale = 1 + time_diff * time_weight
            order_scale = 1 + calculate_single_inversion_distance(perm_array) * order_weight

            # any new minimum weighted dtw must beat the current dtw / product of scales
            dtw_to_beat = dtw_min / (distance_scale * time_scale * order_scale)
            dtw_val = quick_dtw(user_array, traj_match, dtw_to_beat)
            weighted_dtw_val = dtw_val * distance_scale * time_scale * order_scale

            if weighted_dtw_val < dtw_min:
                dtw_min = weighted_dtw_val
                min_id = traj_id

    # re-fetch just the best match to plot it
    sql_select = """
            SELECT latitude, longitude, datetime, id
            FROM taxi_trips
            WHERE id = ?
            ORDER BY seq ASC;
    """

    cursor.execute(sql_select, min_id)
    traj_match = cursor.fetchall()
    for row in traj_match:
        new_row = {'latitude': row[0], 'longitude': row[1], 'timestamp': row[2], 'id': row[3]}
        all_traj.loc[len(all_traj)] = new_row
    
    plot_trajectories(all_traj)

    conn.commit()
    cursor.close()
    conn.close()

def plot_trajectories(trajectories):
    apikey = "AIzaSyA2LDQ5OjMPm8TmX290egK1uCv1o80AJvw"

    gmap = gmplot.GoogleMapPlotter(trajectories['latitude'][0], trajectories['longitude'][0], 13, apikey=apikey)

    first = True

    for traj in trajectories.id.unique():
        latitude_list = trajectories[trajectories['id']==traj]['latitude']
        longitude_list = trajectories[trajectories['id']==traj]['longitude']

        gmap.scatter (latitude_list, longitude_list, '#FF0000', size = 40, marker = False)
        #color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        color = '#BE398D'
        edge_width = 4
        if first:
            color = '#000000'
            edge_width = 6
            first = False
        gmap.plot(latitude_list, longitude_list, color, edge_width = edge_width )
    
    map_path = os.getcwd()
    outpath = os.path.join(map_path, 'userInput.html')
    gmap.draw(outpath)
    
    webbrowser.open_new_tab('userInput.html')

def test():
    usertraj = get_trajectory()
    time_val, distance_val, order_val = get_parameters()
    result = find_intersections(usertraj)
    weighted_dtw_on_intersections(usertraj, result, time_val, distance_val, order_val)

def test_loop():
    for i in range(1, 30):
        file_path = 'C:\\Users\\TinBu\\OneDrive\\Desktop\\TCSS 565\\SpatialDBProject\\User_Trajectories\\user' + str(i) + '.csv'
        usertraj = read_file(file_path)
        time_val, distance_val, order_val = random.randint(0,10), random.randint(0,10), random.randint(0, 10)
        result = find_intersections(usertraj)
        weighted_dtw_on_intersections(usertraj, result, time_val, distance_val, order_val)

def test_random_loop(num):
    # current number of trajectories in database
    numtraj = 9717
    for i in range(1, num):
        usertraj = get_random_trajectory(numtraj)
        time_val, distance_val, order_val = random.randint(0,10), random.randint(0,10), random.randint(0, 10)
        result = find_intersections(usertraj)
        weighted_dtw_on_intersections(usertraj, result, time_val, distance_val, order_val)

#test_random_loop(int(5))
#test_loop()
test()
