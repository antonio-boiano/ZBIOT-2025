import os
import pandas as pd

dataset_dir = "./Data"
aggregated_output_dir_duration = "6-Merged_Data/6-Merged_sequence_data_fix_durations"

os.makedirs(aggregated_output_dir_duration, exist_ok=True)

categories = ["Idle", "Physical_Interaction", "Power", "Scenario", "Web_Interaction"]
topologies = ["Topology_A", "Topology_B"]

window_sizes_duration = [1, 2, 3, 5]

for topology in topologies:
    for window_size in window_sizes_duration:
        aggregated_data_duration = []

        for category in categories:
            sequence_data_path_duration = os.path.join(dataset_dir, category, topology, "5-Sequence_Data_Fix_Duration")

            if os.path.exists(sequence_data_path_duration):
                for file in os.listdir(sequence_data_path_duration):
                    file_path = os.path.join(sequence_data_path_duration, file)
                    if file.endswith(f"_group_sequence_{window_size}s.csv"):
                        try:
                            df = pd.read_csv(file_path)
                            df = df[df["Device Type"] != "Unknown"]
                            df = df[df["Device Type"] != "Broadcast"]
                            df = df[df["Device Type"] != "Temperature"]
                            df = df[df["Device Type"] != "Vibration"]
                            for col in df.columns:
                                if df[col].isnull().any():
                                    df[col] = df[col].fillna(-1)

                            aggregated_data_duration.append(df)
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")

        # Merge and save the data if available
        if aggregated_data_duration:
            aggregated_df_duration = pd.concat(aggregated_data_duration, ignore_index=True)
            output_file_name_duration = f"{topology}_fix_duration_{window_size}s.csv"
            output_file_path_duration = os.path.join(aggregated_output_dir_duration, output_file_name_duration)
            aggregated_df_duration.to_csv(output_file_path_duration, index=False, encoding="utf-8")
            print(f"Aggregated duration data saved to: {output_file_path_duration}")
        else:
            print(f"No data available for topology: {topology}, window size: {window_size}s (duration)")
