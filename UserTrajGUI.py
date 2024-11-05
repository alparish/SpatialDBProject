
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
from geopy.distance import geodesic
from datetime import datetime
from itertools import combinations
from datetime import timedelta

def read_file(file_path):
    user_file = pd.read_csv(file_path, header=None)
    user_file.rename(columns={0: 'latitude', 1: 'longitude', 2: 'timestamp'}, inplace=True)
    user_file['id'] = int(0)
    user_file['timestamp'] = pd.to_datetime(user_file['timestamp'])
    print(user_file)
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
            print(user_file)
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
            
def get_parameters():
    wait_times = ['5 min', '15 min', '30 min', '45 min', '1 hour', '2 hours']
    walk_distance = ['500 ft', '1000 ft', '1/2 mile', '1 mile', '2 mile']
    order = ['No', 'Yes']
    
    layout_param = [[sg.Text("How far are you willing to travel to start carpooling?")],
           [sg.Combo(walk_distance, default_value='1 mile', key='-DIST-')],
           [sg.Text("How long are you willing to wait to start carpooling?")],
           [sg.Combo(wait_times, default_value='30 min', key='-TIME-')],
           [sg.Text("Do you want to consider rides that visit your stops out of order?")],
           [sg.Combo(order, default_value='No', key='-Order-')],
           [sg.Button('Go', key='Go'), sg.Button('Cancel', key='Cancel')]]
    
    param_window = sg.Window('Establish Parameters', layout_param, font='20')
    
    while True:
        event, values = param_window.read()
        
        if event == 'Go':
            if values['-TIME-']:
                time = values['-TIME-']
            else:
                time = '30 min'
            if values['-DIST-']:
                dist = values['-DIST-']
            else:
                dist = '1 mile'
            if values['-Order-']:
                ord = values['-Order-']
            else:
                ord = 'No'
            param_window.close()
            return time, dist, ord
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
    print("Connected to the database")

    #df = pd.read_sql('SELECT t.id, t.seq, t.longitude, t.latitude FROM taxi_trips as t', conn)

    taxi_id = 0
    trip_id = 0
    traj_id = 0
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
        SELECT TOP 3 T2.Id, Area = T1.ShapeGeography.STBuffer(20).STIntersection(T2.ShapeGeography.STBuffer(20)).STArea()
        FROM Trajectories T1 JOIN Trajectories T2
        ON T1.ShapeGeography.STBuffer(20).STIntersects(T2.ShapeGeography.STBuffer(20))=1 AND T1.Id = 0 AND T2.Id > 0
        ORDER BY Area DESC;
        """
    
    try:
        cursor.execute(sql_intersect)
        result = cursor.fetchall()
    except Exception as e:
        print(f"Error {e}")
        raise

    sql_remove = f'DELETE FROM Trajectories WHERE id={traj_id};'
    cursor.execute(sql_remove)
    conn.commit()
    cursor.close()
    conn.close()

    print(result)

    return result

# DTW Algorithm Implementation
def dtw(trip1, trip2):
    n, m = len(trip1), len(trip2)
    # Initialize the DTW matrix with infinity
    dtw_matrix = np.zeros((n + 1, m + 1))
    dtw_matrix[0, 1:] = float('inf')
    dtw_matrix[1:, 0] = float('inf')

    # Fill the DTW matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            # Calculate distance between points
            cost = geodesic(trip1[i - 1][:2], trip2[j - 1][:2]).miles
            dtw_matrix[i, j] = cost**2 + min(dtw_matrix[i - 1, j],
                                          dtw_matrix[i, j - 1],   
                                          dtw_matrix[i - 1, j - 1])
    # Normalize the DTW distance
    dtw_distance = dtw_matrix[n, m]
    normalized_dtw = np.sqrt(dtw_distance / max(n, m))

    # Return the normalized DTW distance
    return normalized_dtw

def dtw_on_intersections(usertraj, result):
    user_lat = usertraj['latitude']
    user_long = usertraj['longitude']

    server = 'localhost'
    database = 'master'
    
    all_traj = usertraj.copy()
    user_array = usertraj.to_numpy()

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
    print("Connected to the database")

    dtw_min = float('inf')
    min_id = 0
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
        print(f"DTW on user trajectory and trajectory {traj_id}:")
        dtw_val = dtw(user_array, traj_match)
        print(dtw_val)

        if dtw_val < dtw_min:
            dtw_min = dtw_val
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
        new_row = {'latitude':row[0], 'longitude':row[1], 'timestamp':row[2], 'id':row[3]}
        all_traj.loc[len(all_traj)] = new_row

    #print(all_traj)
    plot_trajectories(all_traj)

    conn.commit()
    cursor.close()
    conn.close()
    

def plot_trajectories(trajectories):
    apikey = "AIzaSyCahw5aOz74AiJwqSss5XN-S7oMuGp7cxU"

    gmap = gmplot.GoogleMapPlotter(trajectories['latitude'][0], trajectories['longitude'][0], 13, apikey=apikey)

    for traj in trajectories.id.unique():
        latitude_list = trajectories[trajectories['id']==traj]['latitude']
        longitude_list = trajectories[trajectories['id']==traj]['longitude']

        gmap.scatter (latitude_list, longitude_list, '#FF0000', size = 40, marker = False)
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        if traj == 0:
            color = '#000000'
        gmap.plot(latitude_list, longitude_list, color, edge_width = 5 )
    
    map_path = os.getcwd()
    outpath = os.path.join(map_path, 'userInput.html')
    gmap.draw(outpath)
    
    webbrowser.open_new_tab('userInput.html')

def test():
    usertraj = get_trajectory()
    time_constraint, distance_constraint, order_constraint = get_parameters()
    print("The user trajectory:")
    print(usertraj)
    print("The parameters for the search:")
    print(time_constraint, distance_constraint, order_constraint)

    #plot_trajectories(usertraj)
    result = find_intersections(usertraj)
    dtw_on_intersections(usertraj, result)

def test_loop():
    for i in range(1, 30):
        file_path = 'C:\\Users\\TinBu\\OneDrive\\Desktop\\TCSS 565\\SpatialDBProject\\User_Trajectories\\user' + str(i) + '.csv'
        usertraj = read_file(file_path)
        result = find_intersections(usertraj)
        dtw_on_intersections(usertraj, result)

test_loop()

'''
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Check input and output directory paths.')

	parser.add_argument('-i', '--input_dir', required=True, type=check_valid_directory,
						help='Path to the input directory')
	parser.add_argument('-o', '--output_dir', required=True, type=check_valid_directory,
						help='Path to the output directory')

	args = parser.parse_args()
	generate_outputs(args.input_dir, args.output_dir)
'''