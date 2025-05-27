import os
import pandas as pd

dataset_dir = "D:\ZBIOT-2025\Dataset"

long_path = os.path.join(dataset_dir, "Long captures")

# New File to save the Combined Data
combined_data_path = os.path.join(long_path, "3-Combined_dataset")
os.makedirs(combined_data_path, exist_ok=True)
# The groundtruth file
groundtruth_folder = os.path.join(long_path, "1-Groundtruth")
# The Information extracted from the pcap file
for file in os.listdir(os.path.join(long_path, "2-Information_From_PCAP")):
    base_name = file.replace('_keyinformation.csv', '')
    groundtruth_file_path = os.path.join(groundtruth_folder, f"{base_name}_groundtruth.csv")
    output_file_path = os.path.join(combined_data_path, f"{base_name}_combined.csv")

    try:
        groundtruth_df = pd.read_csv(groundtruth_file_path,
                                     usecols=[ "Device Name","Device Type","Device Name Destination","Device Type Destination"])
    except ValueError:
        continue

    extracted_df = pd.read_csv(os.path.join(long_path, "2-Information_From_PCAP", file))
    combined_df = pd.concat([groundtruth_df, extracted_df], axis=1)
    combined_df.to_csv(output_file_path, index=False, encoding="utf-8")
    print(f"Saved combined file to: {output_file_path}")