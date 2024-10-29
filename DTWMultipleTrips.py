from geopy.distance import geodesic
import numpy as np
from datetime import datetime
from itertools import combinations

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

# Sample Data
def generate_sample_data():
    trips = [
        # (latitude, longitude, timestamp)
        [(37.7749, -122.4194, '2024-01-01 12:00:00'),
         (37.7750, -122.4185, '2024-01-01 12:01:00'),
         (37.7751, -122.4176, '2024-01-01 12:02:00')],
         
        [(37.7861, -122.4195, '2024-01-01 12:00:30'),
         (37.7862, -122.4186, '2024-01-01 12:01:30'),
         (37.7863, -122.4177, '2024-01-01 12:02:30')],

        [(37.7750, -122.4150, '2024-01-01 12:15:00'),
         (37.7760, -122.4140, '2024-01-01 12:16:00'),
         (37.7770, -122.4130, '2024-01-01 12:17:00')],
         
        [(37.7600, -122.4700, '2024-01-01 12:10:00'),
         (37.7610, -122.4690, '2024-01-01 12:11:00'),
         (37.7620, -122.4680, '2024-01-01 12:12:00')],
         
        [(37.7745, -122.4194, '2024-01-01 12:40:00'),
         (37.7755, -122.4185, '2024-01-01 12:41:00'),
         (37.7758, -122.4176, '2024-01-01 12:42:00')],
    ]
    return trips

# Main Function to Run the DTW Calculation
if __name__ == "__main__":
    # Generate sample trajectories
    trips = generate_sample_data()

    # Calculate DTW distances for all combinations of trips
    for (idx1, trip1), (idx2, trip2) in combinations(enumerate(trips, start=1), 2):
        # Calculate distance using geodesic
        distance = geodesic(trip1[0][:2], trip2[0][:2]).miles

        # Parse the starting timestamps
        start_time_trip1 = datetime.strptime(trip1[0][2], '%Y-%m-%d %H:%M:%S')
        start_time_trip2 = datetime.strptime(trip2[0][2], '%Y-%m-%d %H:%M:%S')

        # Calculate the time difference in minutes
        time_difference = abs((start_time_trip1 - start_time_trip2)).total_seconds() / 60

        # Print trip information
        print(f"\nComparing Trip {idx1} and Trip {idx2}:")
        print(f"Starting distance: {distance:.2f} miles")
        print(f"Starting time difference: {time_difference:.2f} minutes")

        # Check for distance > 1 mile and time difference > 30 minutes
        if (distance > 1 or time_difference > 30):
            if distance > 1:
                print("Condition met: Distance > 1 mile")
            if time_difference > 30:
                print("Condition met: Time difference > 30 minutes")
        else:
            # Calculate DTW distance between the two trips
            dtw_distance = dtw(trip1[1:], trip2[1:])

            # Output the result
            print(f"DTW Distance between the trips: {dtw_distance:.2f}")
