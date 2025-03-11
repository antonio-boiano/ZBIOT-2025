import os
import pandas as pd

dataset_dir = "./Data"

output_a_file = "Aggregated_Data/Combined_Topology_A.csv"
output_b_file = "Aggregated_Data/Combined_Topology_B.csv"

all_data_a = []
all_data_b = []

for category in ["Idle", "Physical_Interaction", "Scenario", "Web_Interaction"]:
    category_path = os.path.join(dataset_dir, category)

    for topology in ["Topology_A", "Topology_B"]:
        topology_path = os.path.join(category_path, topology)
        raw_data_path = os.path.join(topology_path, "Raw_dataset")

        if os.path.isdir(raw_data_path):
            for file in os.listdir(raw_data_path):
                if file.endswith(".csv"):
                    file_path = os.path.join(raw_data_path, file)
                    df = pd.read_csv(file_path)
                    if topology == "Topology_A":
                        all_data_a.append(df)
                    elif topology == "Topology_B":
                        all_data_b.append(df)

if all_data_a:
    combined_a = pd.concat(all_data_a, axis=0)
    combined_a.to_csv(output_a_file, index=False, encoding="utf-8")
    print(f"Topology_A saved: {output_a_file}")

if all_data_b:
    combined_b = pd.concat(all_data_b, axis=0)
    combined_b.to_csv(output_b_file, index=False, encoding="utf-8")
    print(f"Topology_B saved: {output_b_file}")
