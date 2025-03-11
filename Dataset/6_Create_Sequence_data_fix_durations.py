import pandas as pd
import os
import numpy as np

input_dir = "./Data/Aggregated_Data"
output_dir = "./Data/Sequence_Data"
os.makedirs(output_dir, exist_ok=True)

input_files = ["Combined_Topology_A.csv", "Combined_Topology_B.csv"]
window_size = 0.5

def parse_time(x):
    try:
        time_part = x.split(' ')[-1]
        parts = time_part.split(':')

        if len(parts) == 3:
            hours = int(parts[0]) * 3600
            minutes = int(parts[1]) * 60
            seconds = float(parts[2])
            return hours + minutes + seconds
        else:
            raise ValueError
    except Exception:
        return np.nan

for input_file in input_files:
    input_path = os.path.join(input_dir, input_file)
    data = pd.read_csv(input_path)

    data['Time_in_seconds'] = data['Time'].apply(parse_time)
    result_data = []

    for i in range(len(data)):
        start_time = data.loc[i, 'Time_in_seconds']
        end_time = start_time + window_size

        # Filtering data within [start_time, end_time].
        current_window = data[(data['Time_in_seconds'] >= start_time) & (data['Time_in_seconds'] < end_time)]

        if current_window.empty:
            continue
        first_packet = current_window.iloc[0]
        device_name = first_packet['Device Name']
        device_type = first_packet['Device Type']

        avg_packet_length = current_window['Length'].mean()
        std_packet_length = current_window['Length'].std()
        avg_iat = current_window['Delta Time'].mean()
        std_iat = current_window['Delta Time'].std()
        max_sequence_number = current_window['Sequence Number'].max()
        min_sequence_number = current_window['Sequence Number'].min()
        avg_sequence_number = current_window['Sequence Number'].mean()

        result_data.append([
            device_name, device_type, avg_packet_length, std_packet_length, avg_iat,
            std_iat, max_sequence_number, min_sequence_number, avg_sequence_number
        ])
    result_df = pd.DataFrame(result_data, columns=[
        "Device Name", "Device Type", "Average Packet Length", "Packet Standard Variance", "Average IAT",
        "IAT Standard Variance", "Sequence Number Maximum", "Sequence Number Minimum", "Sequence Number Average"
    ])

    if "Topology_A" in input_file:
        output_file_name = "Sequence_Data_Topology_A_fix_durations.csv"
    else:
        output_file_name = "Sequence_Data_Topology_B_fix_durations.csv"

    output_path = os.path.join(output_dir, output_file_name)
    result_df.to_csv(output_path, index=False, encoding='utf-8')
