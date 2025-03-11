import pandas as pd
import os

input_dir = "./Data/Aggregated_Data"
output_dir = "./Data/Sequence_Data"
os.makedirs(output_dir, exist_ok=True)

input_files = ["Combined_Topology_A.csv", "Combined_Topology_B.csv"]
window_size = 3  # Define window size(how many packets in one window)

for input_file in input_files:
    input_path = os.path.join(input_dir, input_file)
    data = pd.read_csv(input_path)

    result_data = []

    for i in range(len(data) - window_size + 1):
        current_window = data.iloc[i:i + window_size]

        avg_packet_length = current_window.iloc[:, 4].mean()
        std_packet_length = current_window.iloc[:, 4].std()
        avg_iat = current_window.iloc[:, 3].mean()
        std_iat = current_window.iloc[:, 3].std()
        max_sequence_number = current_window.iloc[:, 8].max()
        min_sequence_number = current_window.iloc[:, 8].min()
        avg_sequence_number = current_window.iloc[:, 8].mean()
        device_name = current_window.iloc[0, 0]
        device_type = current_window.iloc[0, 1]

        result_data.append([
            device_name, device_type, avg_packet_length, std_packet_length,
            avg_iat, std_iat, max_sequence_number, min_sequence_number, avg_sequence_number
        ])

    result_df = pd.DataFrame(result_data, columns=[
        "Device Name", "Device Type", "Average Packet Length", "Packet Standard Variance", "Average IAT",
        "IAT Standard Variance", "Sequence Number Maximum", "Sequence Number Minimum", "Sequence Number Average"
    ])

    if "Topology_A" in input_file:
        output_file_name = "Sequence_Data_Topology_A_fix_packets.csv"
    else:
        output_file_name = "Sequence_Data_Topology_B_fix_packets.csv"

    output_path = os.path.join(output_dir, output_file_name)
    result_df.to_csv(output_path, index=False, encoding='utf-8')


