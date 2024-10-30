CREATE TABLE taxi_trips (
    taxi_id INT NOT NULL,
    trip_id INT NOT NULL,
    datetime DATETIME2 NOT NULL,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    location GEOGRAPHY NOT NULL,
    CONSTRAINT PK_taxi_trips PRIMARY KEY CLUSTERED (taxi_id, trip_id, datetime)
);