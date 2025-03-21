import os
import pandas as pd

dataset_dir = "./Data"
aggregated_output_dir = "Merged_Data/A_6-Merged_sequence_data_fix_durations"
# aggregated_output_dir = "Merged_Data/A_6-Merged_sequence_data_fix_packets"

os.makedirs(aggregated_output_dir, exist_ok=True)

categories = ["Idle", "Physical_Interaction", "Scenario", "Web_Interaction"]
topologies = ["Topology_A", "Topology_B"]

for topology in topologies:
    aggregated_data = []

    for category in categories:
        sequence_data_path = os.path.join(dataset_dir, category, topology, "A_5_2-Sequence_Data_Fix_Duration")
        # sequence_data_path = os.path.join(dataset_dir, category, topology, "A_5_1-Sequence_Data_Fix_Packets")


        if not os.path.exists(sequence_data_path):
            print(f"Directory not found: {sequence_data_path}")
            continue

        for file in os.listdir(sequence_data_path):
            file_path = os.path.join(sequence_data_path, file)

            if not file.endswith(".csv"):
                continue

            try:
                df = pd.read_csv(file_path)

                # Filter out lines where "Device Name" is "Unknown".
                df = df[df["Device Name"] != "Unknown"]

                # Add "File Name" column
                original_file_base = os.path.splitext(file.replace("_group_sequence", ".pcapng"))[0]
                df.insert(2, "File Name", f"{category}_{topology}_{original_file_base}")
                aggregated_data.append(df)

            except Exception as e:
                print(f"Error processing file {file_path}: {e}")

    if aggregated_data:
        aggregated_df = pd.concat(aggregated_data, ignore_index=True)
    else:
        print(f"No data available for topology: {topology}")
        continue

    output_file_name = f"{topology}_fix_duration.csv"
    # output_file_name = f"{topology}_fix_packets.csv"
    output_file_path = os.path.join(aggregated_output_dir, output_file_name)
    aggregated_df.to_csv(output_file_path, index=False, encoding="utf-8")
    print(f"Aggregated data saved to: {output_file_path}")
