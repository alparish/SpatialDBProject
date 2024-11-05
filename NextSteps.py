import pandas as pd
import pyodbc

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

df = pd.read_sql('SELECT t.taxi_id, t.trip_id, t.longitude, t.latitude FROM taxi_trips as t', conn)

print(df)
