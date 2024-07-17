import numpy as np
import csv
import pandas as pd

def read_data(filename):
    df = pd.read_csv(filename, header=None, names=['icao24', 'lat', 'lon', 'timestamp'])
    return df

def initialize_kalman(lat_lons):
    initial_lat = lat_lons[0][0]
    initial_lon = lat_lons[0][1]
    x = np.array([initial_lat, initial_lon, 0, 0])  # Initial state with zero velocity

    P = np.eye(4) * 1000  # Large initial uncertainty

    Q = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0],
                  [0, 0, 0.01, 0],
                  [0, 0, 0, 0.01]])  # Process noise covariance matrix

    R = np.array([[0, 0],
                  [0, 0]])  # Measurement noise covariance matrix

    return x, P, Q, R

def kalman_filter(lat_lons):
    dt = 1  
    F = np.array([[1, 0, dt, 0],
                  [0, 1, 0, dt],
                  [0, 0, 1, 0],
                  [0, 0, 0, 1]])

    H = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0]])

    x, P, Q, R = initialize_kalman(lat_lons)
    predictions = []

    for lat_lon in lat_lons:
        lat = lat_lon[0]
        lon = lat_lon[1]
        # Measurement update (correction)
        z = np.array([lat, lon])
        y = z - H.dot(x)  # Use only lat and lon from state vector
        S = H.dot(P).dot(H.T) + R
        K = P.dot(H.T).dot(np.linalg.inv(S))
        x = x + K.dot(y)
        P = (np.eye(4) - K.dot(H)).dot(P)

        # Predict (projection)
        x = F.dot(x)
        P = F.dot(P).dot(F.T) + Q

        predictions.append((x[0], x[1]))

    return predictions

def process_planes(df):
    results = {}
    for icao24, group in df.groupby('icao24'):
        lat_lons = group[['lat', 'lon', 'timestamp']].values.tolist()  # Convert DataFrame to list of tuples
        sorted_lat_lons = sorted(lat_lons, key=lambda x: x[2])  # Sort by timestamp
        filtered_lat_lons = kalman_filter(sorted_lat_lons)
        results[icao24] = filtered_lat_lons
    return results

def main():
    filename = '/home/eheidrich/Documents/Flight-Tracker-Simulator/sample_recv/positions.txt'
    df = read_data(filename)
    results = process_planes(df)

    for icao24, filtered_lat_lons in results.items():
        print(f"Plane ID: {icao24}")
        for i, (filtered_lat, filtered_lon) in enumerate(filtered_lat_lons[:-1]):
            original = df[df['icao24'] == icao24].iloc[i]
            print(f"Original: ({original['lat']}, {original['lon']}), Filtered: ({filtered_lat:.6f}, {filtered_lon:.6f})")
        # Print the predicted next latitude and longitude
        next_prediction = filtered_lat_lons[-1]
        print(f"Predicted Next: (Lat: {next_prediction[0]:.6f}, Lon: {next_prediction[1]:.6f})")

if __name__ == "__main__":
    main()
