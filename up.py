import pandas as pd
import os
import random

SAVE_PATH = './'
os.makedirs(SAVE_PATH, exist_ok=True)

# --- 1. Create stations.csv with full names and locations ---
station_data = {
    'code': ['CSTM', 'DR', 'KYN', 'KJT', 'LNL', 'TGN', 'DVR', 'KAD', 'SVJR', 'PUNE'],
    'full_name': ['Mumbai CST', 'Dadar', 'Kalyan', 'Karjat', 'Lonavala', 'Talegaon', 'Dehu Road', 'Khadki', 'Shivaji Nagar', 'Pune Jn'],
    'lat': [18.9398, 19.0186, 19.2437, 18.91, 18.7546, 18.7359, 18.6735, 18.5682, 18.5308, 18.5286],
    'lon': [72.8355, 72.8448, 73.1355, 73.3235, 73.4072, 73.6757, 73.7402, 73.8507, 73.8525, 73.874]
}
stations_df = pd.DataFrame(station_data)
stations_df.to_csv(os.path.join(SAVE_PATH, 'stations.csv'), index=False)
print("✅ Successfully created 'stations.csv'.")

# --- 2. Create routes.csv with distances between stations ---
route_list = []
station_codes = station_data['code']
for i in range(len(station_codes) - 1):
    station_from = station_codes[i]
    station_to = station_codes[i+1]
    route_list.append({
        'station_from': station_from,
        'station_to': station_to,
        'distance_km': round(random.uniform(8, 60), 1) # Random distance
    })
routes_df = pd.DataFrame(route_list)
routes_df.to_csv(os.path.join(SAVE_PATH, 'routes.csv'), index=False)
print("✅ Successfully created 'routes.csv'.")