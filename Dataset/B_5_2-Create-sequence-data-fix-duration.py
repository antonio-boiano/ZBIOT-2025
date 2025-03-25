import os
import pandas as pd
import numpy as np

WINDOW_SIZE_IN_SECONDS = 1

dataset_dir = "./Data"

def parse_time(x):
    try:
        time_part = x.split(' ')[-1]
        time_parts = time_part.split(':')
        if len(time_parts) == 3:
            hours = int(time_parts[0]) * 3600
            minutes = int(time_parts[1]) * 60
            seconds = float(time_parts[2])
            return hours + minutes + seconds
    except Exception as e:
        print(f"Error parsing time: {x}, Error: {e}")
        return np.nan


for category in ["Idle", "Physical_Interaction", "Scenario", "Web_Interaction"]:
    category_path = os.path.join(dataset_dir, category)
    for topology in ["Topology_A", "Topology_B"]:
        topology_path = os.path.join(category_path, topology)

        for device_name_folder in os.listdir(topology_path):
            raw_dataset_path = os.path.join(topology_path, device_name_folder)

            if not os.path.isdir(raw_dataset_path) or not device_name_folder.startswith("B_4-Sort_dataset"):
                continue

            sequence_output_path = os.path.join(topology_path, "B_5_2-Sequence_Data_Fix_Duration")
            os.makedirs(sequence_output_path, exist_ok=True)

            for file in os.listdir(raw_dataset_path):
                file_path = os.path.join(raw_dataset_path, file)
                if not file.endswith("_sort.csv"):
                    continue

                try:
                    df = pd.read_csv(file_path)

                    df["Time_in_seconds"] = df["Time"].apply(parse_time)
                    df = df.sort_values(by=["Device Name ZigBee", "Time_in_seconds"], ascending=[True, True])

                    result_data = []

                    for group, group_data in df.groupby("Device Name ZigBee", sort=False):
                        start_time = group_data["Time_in_seconds"].min()
                        step_size = 1

                        while start_time <= group_data["Time_in_seconds"].max():
                            end_time = start_time + WINDOW_SIZE_IN_SECONDS
                            current_window = group_data[
                                (group_data["Time_in_seconds"] >= start_time) &
                                (group_data["Time_in_seconds"] < end_time)
                            ]

                            if not current_window.empty:
                                avg_packet_length = current_window["Length"].mean()
                                std_packet_length = current_window["Length"].std()
                                std_packet_length = std_packet_length if pd.notna(std_packet_length) else 0
                                avg_iat = current_window["Delta Time"].mean()
                                std_iat = current_window["Delta Time"].std()
                                std_iat = std_iat if pd.notna(std_iat) else 0
                                max_sequence_number = current_window["Sequence Number"].max()
                                min_sequence_number = current_window["Sequence Number"].min()
                                avg_sequence_number = current_window["Sequence Number"].mean()

                                result_data.append([
                                    group_data["Device Name ZigBee"].iloc[0],
                                    group_data["Device Type ZigBee"].iloc[0],
                                    avg_packet_length,
                                    std_packet_length,
                                    avg_iat,
                                    std_iat,
                                    max_sequence_number,
                                    min_sequence_number,
                                    avg_sequence_number
                                ])

                            start_time += step_size

                    result_df = pd.DataFrame(result_data, columns=[
                        "Device Name", "Device Type", "Average Packet Length", "Packet Standard Variance",
                        "Average IAT", "IAT Standard Variance", "Sequence Number Maximum",
                        "Sequence Number Minimum", "Sequence Number Average"
                    ])

                    new_file_name = file.replace("_sort", "_sort_sequence")
                    output_file_path = os.path.join(sequence_output_path, new_file_name)
                    result_df.to_csv(output_file_path, index=False, encoding="utf-8")
                    print(f"Generated feature sequence saved to: {output_file_path}")

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
