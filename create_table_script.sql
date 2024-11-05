IF OBJECT_ID('dbo.taxi_trips', 'U') IS NOT NULL
DROP TABLE dbo.taxi_trips
GO


CREATE TABLE taxi_trips (
    taxi_id INT NOT NULL,
    trip_id INT NOT NULL,
    datetime DATETIME2 NOT NULL,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    location GEOGRAPHY NOT NULL,
    CONSTRAINT PK_taxi_trips PRIMARY KEY CLUSTERED (taxi_id, trip_id, datetime)
);

SELECT t.taxi_id, t.trip_id, t.datetime, t.longitude, t.latitude, t.location
FROM dbo.taxi_trips as t 
GO