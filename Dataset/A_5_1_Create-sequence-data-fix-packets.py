import os
import pandas as pd
from datetime import datetime

def parse_timestamp(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y/%m/%d %H:%M:%S.%f")
def mad(df):
    return ((df - df.mean()).abs().mean())

def extract_features(current_window):
    if len(current_window) > 1:
        return {
        "Average Packet Length": current_window["Length"].mean(),
        "Packet Standard Variance": current_window["Length"].std(),
        "Maximum Packet Length": current_window["Length"].max(),
        "Minimum Packet Length": current_window["Length"].min(),
        "Median Packet Length": current_window["Length"].median(),
        "Kurtosis Packet Length": current_window["Length"].kurtosis(),
        "Skew Packet Length": current_window["Length"].skew(),
        "Mad Packet Length": mad(current_window["Length"]),
        "Length": len(current_window),
        "Average IAT": current_window["Time"].diff(1).apply(lambda x: x.total_seconds()).mean(),
        "IAT Standard Variance": current_window["Time"].diff(1).apply(lambda x: x.total_seconds()).std(),
        "Maximum IAT": current_window["Time"].diff(1).apply(lambda x: x.total_seconds()).max(),
        "Minimum IAT": current_window["Time"].diff(1).apply(lambda x: x.total_seconds()).min(),
        "Median IAT": current_window["Time"].diff(1).apply(lambda x: x.total_seconds()).median(),
        "Kurtosis IAT": current_window["Time"].diff(1).apply(lambda x: x.total_seconds()).kurtosis(),
        "Skew IAT": current_window["Time"].diff(1).apply(lambda x: x.total_seconds()).skew(),
        "Mad IAT": mad(current_window["Time"].diff(1).apply(lambda x: x.total_seconds()))
    }
    else:
        return None

dataset_dir = "./Data"
window_sizes = [3, 5, 10, 15]

for category in ["Idle", "Physical_Interaction", "Power", "Scenario", "Web_Interaction"]:
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

                    df["Time"] = pd.to_datetime(df["Time"])
                    df["Time_second"] = df["Time"].apply(lambda x: x.timestamp())

                    for window_size in window_sizes:
                        result_data = []
                        for i in range(0, len(df) - window_size + 1):
                            current_window = df.iloc[i:i + window_size]
                            if len(current_window["Group"].unique()) > 1:
                                continue
                            if len(current_window) < window_size:
                                continue

                            current_window.sort_values(by="Time")
                            dev_name = current_window.iloc[0, 0]

                            upl_wind = current_window[current_window["Device Name Destination"]==dev_name]
                            dnl_wind = current_window[current_window["Device Name"] == dev_name]
                            dev_info = {
                                "Device Name": current_window.iloc[0, 0],
                                "Device Type": current_window.iloc[0, 1],
                                "File Name": file_path
                            }
                            dev_df = pd.DataFrame([dev_info])

                            up_dict = extract_features(upl_wind)
                            dn_dict = extract_features(dnl_wind)
                            tot_dict = extract_features(current_window)

                            if up_dict is not None:
                                up_df = pd.DataFrame([up_dict])
                                up_df.columns = ['UP_' + col for col in up_df.columns]
                            else:
                                up_df = pd.DataFrame([{}])

                            if dn_dict is not None:
                                dn_df = pd.DataFrame([dn_dict])
                                dn_df.columns = ['DOWN_' + col for col in dn_df.columns]
                            else:
                                dn_df = pd.DataFrame([{}])

                            if tot_dict is not None:
                                tot_df = pd.DataFrame([tot_dict])
                                tot_df.columns = ['TOT_' + col for col in tot_df.columns]
                            else:
                                tot_df = pd.DataFrame([{}])

                            features_combined_all = pd.concat([dev_df, up_df, dn_df, tot_df], axis=1)
                            result_data.append(features_combined_all.iloc[0])

                        if result_data:
                            result_df = pd.DataFrame(result_data)

                            new_file_name = file.replace("_group", f"_group_sequence_{window_size}")
                            output_file_path = os.path.join(sequence_output_path, new_file_name)
                            result_df.to_csv(output_file_path, index=False, encoding="utf-8")
                            print(f"Generated feature sequence saved to: {output_file_path}")

                except Exception as e:
                    print(f"Error processing file {file_path}: {e}")
