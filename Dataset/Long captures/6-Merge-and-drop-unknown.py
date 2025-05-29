import os
import pandas as pd

dataset_dir = "."
aggregated_output_dir_duration = "6-Merge-and-drop-unknown"
aggregated_data_duration = []
os.makedirs(aggregated_output_dir_duration, exist_ok=True)
window_size = 5

sequence_data_path_duration = os.path.join(dataset_dir, "5-Sequence_Data_Fix_Duration")

if os.path.exists(sequence_data_path_duration):
    for file in os.listdir(sequence_data_path_duration):
        file_path = os.path.join(sequence_data_path_duration, file)
        if file.endswith(f"_sequence_{window_size}s.csv"):
            try:
                df = pd.read_csv(file_path)
                df = df[df["Device Name"] != "Unknown"]
                for col in df.columns:
                    if df[col].isnull().any():
                        df[col] = df[col].fillna(-1)

                aggregated_data_duration.append(df)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

if aggregated_data_duration:
    aggregated_df_duration = pd.concat(aggregated_data_duration, ignore_index=True)
    output_file_name_duration = f"fix_duration_{window_size}s.csv"
    output_file_path_duration = os.path.join(aggregated_output_dir_duration, output_file_name_duration)
    aggregated_df_duration.to_csv(output_file_path_duration, index=False, encoding="utf-8")
    print(f"Aggregated duration data saved to: {output_file_path_duration}")
else:
    print(f"No data available for window size: {window_size}s (duration)")

