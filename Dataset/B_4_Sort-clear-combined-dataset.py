import os
import pandas as pd

dataset_dir = "./Data"

for category in ["Idle", "Physical_Interaction","Power", "Scenario", "Web_Interaction"]:
    category_path = os.path.join(dataset_dir, category)
    for topology in ["Topology_A", "Topology_B"]:
        topology_path = os.path.join(category_path, topology, "3-Combined_dataset")
        saveto_path = os.path.join(category_path, topology, "B_4-Sort_dataset")
        os.makedirs(saveto_path, exist_ok=True)

        for file in os.listdir(topology_path):
            file_path = os.path.join(topology_path, file)
            if not file.endswith(".csv"):
                continue

            try:
                df = pd.read_csv(file_path)

                missing_cols = [col for col in ["Device Name ZigBee", "Time"] if col not in df.columns]
                if missing_cols:
                    print(f"Missing columns {missing_cols} in file: {file_path}")
                    continue

                # Deleting data from the 'Coordinator' device
                df = df[df["Device Name ZigBee"] != "Coordinator"]

                sorted_df = df.sort_values(by=["Device Name ZigBee", "Time"], ascending=[True, True])

                base_name = file.replace('_combined.csv', '_sort.csv')
                output_file_path = os.path.join(saveto_path, base_name)

                sorted_df.to_csv(output_file_path, index=False, encoding="utf-8")

                print(f"Sorted file saved successfully: {output_file_path}")

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
