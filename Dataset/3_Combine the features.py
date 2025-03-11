import os
import pandas as pd

dataset_dir = "./Data"

for category in ["Idle", "Physical_Interaction", "Scenario", "Web_Interaction"]:
    category_path = os.path.join(dataset_dir, category)
    for topology in ["Topology_A", "Topology_B"]:
        topology_path = os.path.join(category_path, topology)

        raw_data_path = os.path.join(topology_path, "Raw_dataset")
        os.makedirs(raw_data_path)

        groundtruth_folder = os.path.join(topology_path, "groundtruth")

        for file in os.listdir(os.path.join(topology_path, "Extracted_Dataset")):

            base_name = file.replace('_extracted.csv', '')

            groundtruth_file_path = os.path.join(groundtruth_folder, f"{base_name}_groundtruth.csv")
            output_file_path = os.path.join(raw_data_path, f"{base_name}_raw.csv")


            try:
                groundtruth_df = pd.read_csv(groundtruth_file_path, usecols=["Device Name", "Device Type"])
            except ValueError:
                continue

            extracted_df = pd.read_csv(os.path.join(topology_path, "Extracted_Dataset", file))

            combined_df = pd.concat([groundtruth_df, extracted_df], axis=1)
            combined_df.to_csv(output_file_path, index=False, encoding="utf-8")
            print(f"Saved combined file to: {output_file_path}")
