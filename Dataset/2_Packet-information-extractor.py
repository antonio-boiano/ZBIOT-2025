import os
import subprocess
import pandas as pd

# Enter the correct tshark address
tshark_path = "D:/Wireshark/tshark.exe"
dataset_dir = "./Data"

for category in ["Idle", "Physical_Interaction","Power", "Scenario", "Web_Interaction"]:
    category_path = os.path.join(dataset_dir, category)
    for topology in ["Topology_A", "Topology_B"]:
        topology_path = os.path.join(category_path, topology)
        if not os.path.exists(topology_path):
            continue

        for file in os.listdir(topology_path):
            file_path = os.path.join(topology_path, file)

            if not os.path.isfile(file_path) or not file.endswith('.pcapng'):
                continue

            print(f"Processing file: {file}")

            output_category_path = os.path.join(topology_path, "2-Information_From_PCAP")
            os.makedirs(output_category_path, exist_ok=True)
            output_file_path = os.path.join(output_category_path, file.split(".")[0] + "_keyinformation.csv")

            try:
                tshark_command = [
                    tshark_path,
                    "-r", file_path,
                    "-T", "fields",  # Output field format
                    "-e", "frame.time",  # time field
                    "-e", "frame.time_delta",  # timing difference
                    "-e", "frame.len",  # Frame Length field
                    "-e", "wpan.src16",  # IEEE Source Address Field
                    "-e", "wpan.dst16",  # IEEE Destination Address Field
                    "-e", "wpan.seq_no",  # Serial number field
                    "-e", "zbee_nwk.src",  # ZigBee Source Address Field
                    "-e", "zbee_nwk.dst",  # ZigBee Destination Address Field
                    "-E", "header=y",  # The output file contains the header
                    "-E", "separator=,",  # Field separators are commas
                    "-E", "quote=d",  # double quote
                    "-E", "occurrence=f"  # Only one occurrence of field data for each record
                ]

                with open(output_file_path, 'w', encoding='utf-8') as output_file:
                    subprocess.run(tshark_command, stdout=output_file, check=True)

                print(f"Saved CSV file to: {output_file_path}")

                df = pd.read_csv(output_file_path)

                new_headers = {
                    "frame.time": "Time",
                    "frame.time_delta": "Delta Time",
                    "frame.len": "Length",
                    "wpan.src16": "Source IEEE",
                    "wpan.dst16": "Destination IEEE",
                    "wpan.seq_no": "Sequence Number",
                    "zbee_nwk.src": "Source ZigBee",
                    "zbee_nwk.dst": "Destination ZigBee"
                }

                df.rename(columns=new_headers, inplace=True)

                df.to_csv(output_file_path, index=False, encoding='utf-8')
                print(f"Renamed headers and saved CSV file to: {output_file_path}")

                df = pd.read_csv(output_file_path)
                # Removal of redundant notes in the time format. The time of different country versions is not the same, pay attention to change
                df[df.columns[0]] = df[df.columns[0]].str.replace(
                    r"\s西欧夏令时|\s西欧标准时间|\s西欧标准时", "", regex=True
                )

                df.to_csv(output_file_path, index=False, encoding='utf-8')
                print(f"Cleaned and saved CSV file to: {output_file_path}")
            except subprocess.CalledProcessError as e:

                print(f"Failed to process file: {file}\nError: {e}")

            except Exception as e:
                print(f"An error occurred while processing: {file}\nError: {e}")
