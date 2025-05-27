import os
import pandas as pd

dataset_dir = "./Data"
aggregated_output_dir_duration = "Merged_Data/A_6-Merged_sequence_data_fix_durations"

os.makedirs(aggregated_output_dir_duration, exist_ok=True)

categories = ["Idle", "Physical_Interaction", "Power", "Scenario", "Web_Interaction"]
topologies = ["Topology_A", "Topology_B"]

window_sizes_duration = [1, 2, 3, 5]

for topology in topologies:
    for window_size in window_sizes_duration:
        aggregated_data_duration = []

        for category in categories:
            sequence_data_path_duration = os.path.join(dataset_dir, category, topology, "A_5_2-Sequence_Data_Fix_Duration")

            if os.path.exists(sequence_data_path_duration):
                for file in os.listdir(sequence_data_path_duration):
                    file_path = os.path.join(sequence_data_path_duration, file)
                    if file.endswith(f"_group_sequence_{window_size}s.csv"):
                        try:
                            df = pd.read_csv(file_path)
                            df = df[df["Device Name"] != "Unknown"]
                            df = df[df["Device Type"] != "Temperature"]
                            df = df[df["Device Type"] != "Vibration"]
                            df = df[df["Device Type"] != "Button"]
                            df = df[df["Device Type"] != "Door"]
                            for col in df.columns:
                                if df[col].isnull().any():
                                    df[col] = df[col].fillna(-1)

                            aggregated_data_duration.append(df)
                        except Exception as e:
                            print(f"Error processing file {file_path}: {e}")

        # 如果有数据，将其合并并保存
        if aggregated_data_duration:
            aggregated_df_duration = pd.concat(aggregated_data_duration, ignore_index=True)
            output_file_name_duration = f"{topology}_fix_duration_{window_size}s.csv"
            output_file_path_duration = os.path.join(aggregated_output_dir_duration, output_file_name_duration)
            aggregated_df_duration.to_csv(output_file_path_duration, index=False, encoding="utf-8")
            print(f"Aggregated duration data saved to: {output_file_path_duration}")
        else:
            print(f"No data available for topology: {topology}, window size: {window_size}s (duration)")



# dataset_dir = "./Data"
# aggregated_output_dir_packet = "Merged_Data/A_6-Merged_sequence_data_fix_packets"
#
# os.makedirs(aggregated_output_dir_packet, exist_ok=True)
#
# categories = ["Idle", "Physical_Interaction", "Power", "Scenario", "Web_Interaction"]
# topologies = ["Topology_A", "Topology_B"]
#
# # window_sizes_packet = [3, 5, 10, 15]
# window_sizes_packet = [10]
#
# for topology in topologies:
#     for window_size in window_sizes_packet:
#         aggregated_data_packet = []
#
#         for category in categories:
#             sequence_data_path_packet = os.path.join(dataset_dir, category, topology, "A_5_1-Sequence_Data_Fix_Packets")
#
#             if os.path.exists(sequence_data_path_packet):
#                 for file in os.listdir(sequence_data_path_packet):
#                     file_path = os.path.join(sequence_data_path_packet, file)
#                     if file.endswith(f"_group_sequence_{window_size}.csv"):
#                         try:
#                             df = pd.read_csv(file_path)
#                             df = df[df["Device Name"] != "Unknown"]
#                             # df = df[df["Device Type"] != "Temperature"]
#                             # df = df[df["Device Type"] != "Vibration"]
#                             original_file_base = os.path.splitext(file.replace("_group_sequence", ".pcapng"))[0]
#                             # df.insert(2, "File Name", f"{category}_{topology}_{original_file_base}_{window_size}")
#                             aggregated_data_packet.append(df)
#                         except Exception as e:
#                             print(f"Error processing file {file_path}: {e}")
# for topology in topologies:
#     for window_size in window_sizes_packet:
#         aggregated_data_packet = []
#
#         for category in categories:
#             sequence_data_path_packet = os.path.join(dataset_dir, category, topology, "A_5_1-Sequence_Data_Fix_Packets")
#
#             if os.path.exists(sequence_data_path_packet):
#                 for file in os.listdir(sequence_data_path_packet):
#                     file_path = os.path.join(sequence_data_path_packet, file)
#                     if file.endswith(f"_group_sequence_{window_size}.csv"):
#                         try:
#                             df = pd.read_csv(file_path)
#                             df = df[df["Device Name"] != "Unknown"]
#
#                             # 遍历每列进行分类填充
#                             for col in df.columns:
#                                 if df[col].isnull().any():
#                                     df[col] = df[col].fillna(-1)
#
#                             aggregated_data_packet.append(df)
#
#                         except Exception as e:
#                             print(f"Error processing file {file_path}: {e}")
#
#         # 如果有数据，将其合并并保存
#         if aggregated_data_packet:
#             aggregated_df_packet = pd.concat(aggregated_data_packet, ignore_index=True)
#             output_file_name_packet = f"{topology}_fix_packets_{window_size}.csv"
#             output_file_path_packet = os.path.join(aggregated_output_dir_packet, output_file_name_packet)
#             aggregated_df_packet.to_csv(output_file_path_packet, index=False, encoding="utf-8")
#             print(f"Aggregated packet data saved to: {output_file_path_packet}")
#         else:
#             print(f"No data available for topology: {topology}, window size: {window_size} (packets)")


