import pandas as pd
import pyodbc

result_df = pd.read_csv('processed_dataset.csv')

def insert_taxi_data(df, server, database):
    conn_str = (
        'Driver={ODBC Driver 18 for SQL Server};'
        f'Server={server};'
        f'Database={database};'
        'Trusted_Connection=yes;'
        'TrustServerCertificate=yes;'
    )
    
    try:
        # Create connection
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        print("Connected to the database")
        
        rows_processed = 0
        traj_id = 0
        current_taxi = 0
        current_trip = 0
        line_string = ''
        num_points = 0
        
        # SQL insert statement using geography::Point
        insert_trajectories = """
            INSERT INTO Trajectories
                (id, Shape, ShapeGeography)
            VALUES 
                (?, ?, geography::STLineFromText(?, 4326).MakeValid())
            """
        
        # SQL insert statement using geography::Point
        insert_taxi_trips = """
        INSERT INTO taxi_trips
            (id, seq, datetime, longitude, latitude, location)
        VALUES 
            (?, ?, ?, ?, ?, geography::Point(?, ?, 4326))
        """
        for _, row in df.iterrows():
            if current_taxi == 0:
                # first trajectory
                current_taxi = int(row['taxi_id'])
                current_trip = int(row['trip_id'])
                traj_id = 1
                line_string = str(row['longitude']).strip() + ' ' + str(row['latitude']).strip()
                num_points = 1
                try:
                    cursor.execute(
                        insert_taxi_trips,
                        traj_id,
                        num_points,
                        row['datetime'],
                        float(row['longitude']),
                        float(row['latitude']),
                        float(row['latitude']),
                        float(row['longitude'])
                    )
                except Exception as e:
                    print(f"Error inserting row {row['taxi_id']}, {row['trip_id']}: {str(e)}")
                    raise
            elif current_taxi == int(row['taxi_id']) and current_trip == int(row['trip_id']):
                # another point on the current trajectory
                line_string = line_string + ',' + str(row['longitude']).strip() + ' ' + str(row['latitude']).strip()
                num_points += 1
                try:
                    cursor.execute(
                        insert_taxi_trips,
                        traj_id,
                        num_points,
                        row['datetime'],
                        float(row['longitude']),
                        float(row['latitude']),
                        float(row['latitude']),
                        float(row['longitude'])
                    )
                except Exception as e:
                    print(row)
                    print(f"Error inserting row {row['taxi_id']}, {row['trip_id']}, {num_points}: {str(e)}")
                    raise
            else:
                # new taxi and/or new trip, either way, new trajectory
                # insert the old (if at least one point) and start the new
                line_string = 'LINESTRING(' + line_string + ')'
                if num_points > 1:
                    try: 
                        cursor.execute(
                            insert_trajectories,
                            traj_id,
                            line_string,
                            line_string
                        )
                    except Exception as e:
                        print(f"Error inserting row {row['taxi_id']}, {row['trip_id']}, {row['datetime']}: {str(e)}")
                        raise
                current_taxi = int(row['taxi_id'])
                current_trip = int(row['trip_id'])
                traj_id += 1
                line_string = str(row['longitude']).strip() + ' ' + str(row['latitude']).strip()
                num_points = 1
                try:
                    cursor.execute(
                        insert_taxi_trips,
                        traj_id,
                        num_points,
                        row['datetime'],
                        float(row['longitude']),
                        float(row['latitude']),
                        float(row['latitude']),
                        float(row['longitude'])
                    )
                except Exception as e:
                    print(f"Error inserting row {row['taxi_id']}, {row['trip_id']}: {str(e)}")
                    raise
                
            rows_processed += 1
            if rows_processed % 100 == 0:  # Print progress every 100 rows
                print(f"Processed {rows_processed} rows")
        # insert last trajectory
        line_string = 'LINESTRING(' + line_string + ')'
        if num_points > 1:
            try: 
                cursor.execute(
                    insert_trajectories,
                    traj_id,
                    line_string,
                    line_string
                )
            except Exception as e:
                print(f"Error inserting row {row['taxi_id']}, {row['trip_id']}, {row['datetime']}: {str(e)}")
                raise
        # Commit the transaction and close connections
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Data insertion completed successfully. Total rows processed: {rows_processed}")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        raise

server = 'localhost'
database = 'master'


insert_taxi_data(result_df, server, database)