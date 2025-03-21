import os
import pandas as pd

dataset_dir = "./Data"
hash_index_dict = {}
current_index = 0

WINDOW_SIZE = 5  # 滑动窗口大小

for category in ["Idle", "Physical_Interaction", "Scenario", "Web_Interaction"]:
    category_path = os.path.join(dataset_dir, category)
    for topology in ["Topology_A", "Topology_B"]:
        topology_path = os.path.join(category_path, topology)

        for device_name_folder in os.listdir(topology_path):
            raw_dataset_path = os.path.join(topology_path, device_name_folder)

            if not os.path.isdir(raw_dataset_path) or not device_name_folder.startswith(
                    "A_4-Group_dataset"):
                continue

            sequence_output_path = os.path.join(topology_path, "A_5_1-Sequence_Data_Fix_Packets")
            os.makedirs(sequence_output_path, exist_ok=True)

            for file in os.listdir(raw_dataset_path):
                file_path = os.path.join(raw_dataset_path, file)
                if not file.endswith(".csv"):
                    continue
                try:
                    df = pd.read_csv(file_path)
                    if "Group" not in df.columns:
                        print(f"'Group' not found in file: {file_path}")
                        continue
                    result_data = []

                    for i in range(0, len(df) - WINDOW_SIZE + 1):
                        current_window = df.iloc[i:i + WINDOW_SIZE]
                        if len(current_window["Group"].unique()) > 1:
                            continue
                        if len(current_window) < WINDOW_SIZE:
                            continue
                        avg_packet_length = current_window["Length"].mean()
                        std_packet_length = current_window["Length"].std()
                        avg_iat = current_window["Delta Time"].mean()
                        std_iat = current_window["Delta Time"].std()
                        max_sequence_number = current_window["Sequence Number"].max()
                        min_sequence_number = current_window["Sequence Number"].min()
                        avg_sequence_number = current_window["Sequence Number"].mean()
                        device_name = current_window.iloc[0, 0]
                        device_type = current_window.iloc[0, 1]

                        result_data.append([
                            device_name, device_type, avg_packet_length, std_packet_length,
                            avg_iat, std_iat, max_sequence_number, min_sequence_number,
                            avg_sequence_number
                        ])

                    if result_data:
                        result_df = pd.DataFrame(result_data, columns=[
                            "Device Name", "Device Type", "Average Packet Length",
                            "Packet Standard Variance",
                            "Average IAT",
                            "IAT Standard Variance", "Sequence Number Maximum", "Sequence Number Minimum",
                            "Sequence Number Average"
                        ])
                        new_file_name = file.replace("_group", "_group_sequence")
                        output_file_path = os.path.join(sequence_output_path, new_file_name)
                        result_df.to_csv(output_file_path, index=False, encoding="utf-8")
                        print(f"Generated feature sequence saved to: {output_file_path}")

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
