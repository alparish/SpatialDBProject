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
        
        # SQL insert statement using geography::Point
        insert_query = """
        INSERT INTO taxi_trips
            (taxi_id, trip_id, datetime, longitude, latitude, location)
        VALUES 
            (?, ?, ?, ?, ?, geography::Point(?, ?, 4326))
        """
        
        for _, row in df.iterrows():
            try:
                cursor.execute(
                    insert_query,
                    int(row['taxi_id']),
                    int(row['trip_id']),
                    row['datetime'],
                    float(row['longitude']),
                    float(row['latitude']),
                    float(row['latitude']),    # Point takes latitude first
                    float(row['longitude'])     # then longitude
                )
                
                rows_processed += 1
                if rows_processed % 100 == 0:  # Print progress every 100 rows
                    print(f"Processed {rows_processed} rows")
                
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