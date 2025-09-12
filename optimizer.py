# optimizer.py
import pandas as pd
from ortools.sat.python import cp_model
import os


def run_optimization():
    DATASET_PATH = './'
    print(f"Attempting to load datasets from: {os.path.abspath(DATASET_PATH)}")
    try:
        trains_df = pd.read_csv(os.path.join(DATASET_PATH, 'trains.csv'))
        schedules_df = pd.read_csv(os.path.join(DATASET_PATH, 'schedules.csv'))
    except FileNotFoundError as e:
        print(f"❌ FATAL ERROR: Could not find dataset files.\nDetails: {e}")
        return None

    def time_to_seconds(time_str):
        h, m, s = map(int, time_str.split(':'))
        return h * 3600 + m * 60 + s

    schedules_df['arrival_seconds'] = schedules_df['arrival_time'].apply(time_to_seconds)
    schedules_df['departure_seconds'] = schedules_df['departure_time'].apply(time_to_seconds)
    full_schedule_df = pd.merge(schedules_df, trains_df, on='train_id')

    model = cp_model.CpModel()
    horizon = 24 * 3600

    arrival_vars = {}
    departure_vars = {}
    for index, row in full_schedule_df.iterrows():
        key = (row['train_id'], row['station_code'])
        arrival_vars[key] = model.NewIntVar(row['arrival_seconds'], horizon, f'arr_{key[0]}_{key[1]}')
        departure_vars[key] = model.NewIntVar(row['departure_seconds'], horizon, f'dep_{key[0]}_{key[1]}')

    print("⏳ Building model constraints...")

    # LINE 68: Relaxed halt time
    min_halt_seconds = 1 * 60
    for key, arr_var in arrival_vars.items():
        model.Add(departure_vars[key] >= arr_var + min_halt_seconds)

    track_intervals = {}
    for train_id, group in full_schedule_df.sort_values('sequence').groupby('train_id'):
        for i in range(len(group) - 1):
            from_stop = group.iloc[i]
            to_stop = group.iloc[i + 1]
            from_key = (train_id, from_stop['station_code'])
            to_key = (train_id, to_stop['station_code'])

            # LINE 80: Relaxed travel time
            min_travel_seconds = 10 * 60
            travel_duration_var = model.NewIntVar(min_travel_seconds, horizon, f'duration_{from_key}')

            track_segment_id = f"{from_stop['station_code']}_{to_stop['station_code']}_UP"
            if track_segment_id not in track_intervals:
                track_intervals[track_segment_id] = []

            interval = model.NewIntervalVar(
                start=departure_vars[from_key], size=travel_duration_var,
                end=arrival_vars[to_key], name=f'interval_{train_id}_on_{track_segment_id}'
            )
            track_intervals[track_segment_id].append(interval)

    for segment_id, intervals in track_intervals.items():
        if len(intervals) > 1:
            model.AddNoOverlap(intervals)

    total_weighted_delay = []
    for train_id, group in full_schedule_df.groupby('train_id'):
        final_stop = group.loc[group['sequence'].idxmax()]
        final_dep_var = departure_vars[(train_id, final_stop['station_code'])]
        delay = final_dep_var - final_stop['departure_seconds']
        priority = int(final_stop['priority'])
        priority_weight = {1: 10, 2: 5, 3: 1}.get(priority, 1)
        total_weighted_delay.append(delay * priority_weight)
    model.Minimize(sum(total_weighted_delay))

    print("🧠 Solving the optimization model (this may take up to 3 minutes)...")
    solver = cp_model.CpSolver()
    # LINE 110: Increased time limit
    solver.parameters.max_time_in_seconds = 180.0
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print(f"\n✅ SUCCESS! A feasible solution was found.")
        results = []
        for key, arr_var in arrival_vars.items():
            train_id, station = key
            results.append({
                'train_id': train_id,
                'station_code': station,
                'optimized_arrival': pd.to_datetime(solver.Value(arr_var), unit='s').strftime('%H:%M:%S'),
                'optimized_departure': pd.to_datetime(solver.Value(departure_vars[key]), unit='s').strftime('%H:%M:%S')
            })
        return pd.DataFrame(results)
    else:
        print("\n❌ ERROR: No solution was found.")
        return None


if __name__ == '__main__':
    optimized_schedule_df = run_optimization()
    if optimized_schedule_df is not None:
        print("\n--- Optimized Schedule ---")
        print(optimized_schedule_df)