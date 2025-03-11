import os
import pyshark
import pandas as pd

tshark_path = "D:/Wireshark/tshark.exe"

dataset_dir = "./Data"

for category in ["Idle", "Physical_Interaction", "Scenario", "Web_Interaction"]:
    category_path = os.path.join(dataset_dir, category)
    for topology in ["Topology_A", "Topology_B"]:
        topology_path = os.path.join(category_path, topology)

        version = "v1" if topology == "Topology_A" else "v2"

        if not os.path.exists(topology_path):
            continue

        for file in os.listdir(topology_path):
            file_path = os.path.join(topology_path, file)
            if not os.path.isfile(file_path) or not file.endswith('.pcapng'):
                continue

            print(f"Processing file: {file}")

            dict_list = []

            pcap = pyshark.FileCapture(
                file_path,
                tshark_path=tshark_path,
                use_json=True
            )

            for packet in pcap:
                packet_time = packet.frame_info.time

                if (version == "v1" and
                        file == 'physicalInteraction1.pcapng' and packet.number == '2126' or
                        file == 'physicalInteraction2.pcapng' and packet.number == '1556' or
                        file == 'idle2.pcapng' and packet.number == '17066'):
                    continue
                if (version == "v2" and
                        file == 'physicalInteraction1.pcapng' and packet.number == '2502'):
                    continue

                # Processing time format ****Different language versions has different description
                if "000 西欧夏令时" in packet.frame_info.time:
                    packet_time = packet.frame_info.time.replace("000 西欧夏令时", "")
                elif "000 西欧标准时间" in packet.frame_info.time:
                    packet_time = packet.frame_info.time.replace("000 西欧标准时间", "")
                elif "000 西欧标准时" in packet.frame_info.time:
                    packet_time = packet.frame_info.time.replace("000 西欧标准时", "")

                # 初始化变量
                packet_length = packet.frame_info.len
                number_of_layers = len(packet.layers)
                packet_delta_time = None
                packet_sequence_number = None
                packet_source_ieee = None
                packet_destination_ieee = None
                ieee_frame_control_field = None
                packet_source_zigbee = None
                packet_destination_zigbee = None
                extended_packet_source = None
                packet_payload_length = None
                zigbee_frame_control_field = None

                if number_of_layers == 1:
                    try:
                        packet_delta_time = packet.frame_info.time_delta[:-3]
                        packet_sequence_number = packet['WPAN'].seq_no
                        ieee_frame_control_field = packet['WPAN'].fcf
                        packet_source_ieee = packet['WPAN'].src16
                        packet_destination_ieee = packet['WPAN'].dst16
                    except AttributeError:
                        pass

                elif number_of_layers == 2:
                    try:
                        packet_delta_time = packet.frame_info.time_delta[:-3]
                        packet_sequence_number = packet['WPAN'].seq_no
                        ieee_frame_control_field = packet['WPAN'].fcf
                        packet_source_ieee = packet['WPAN'].src16
                        packet_destination_ieee = packet['WPAN'].dst16
                        zigbee_frame_control_field = packet['ZBEE_NWK'].fcf
                        packet_source_zigbee = packet['ZBEE_NWK'].src
                        packet_destination_zigbee = packet['ZBEE_NWK'].dst
                        extended_packet_source = packet['ZBEE_NWK'].zbee_sec_src64
                        packet_payload_length = packet['ZBEE_NWK'].data_len
                    except AttributeError:
                        pass
                    except KeyError:
                        pass

                dict_list.append({'Time': packet_time,
                                  'Delta Time': packet_delta_time,
                                  'Length': packet_length,
                                  'Source IEEE': packet_source_ieee,
                                  'Destination IEEE': packet_destination_ieee,
                                  'FCF IEEE': ieee_frame_control_field,
                                  'Sequence Number': packet_sequence_number,
                                  'Source Zigbee': packet_source_zigbee,
                                  'Destination Zigbee': packet_destination_zigbee,
                                  'FCF Zigbee': zigbee_frame_control_field,
                                  'Payload Length': packet_payload_length,
                                  'Extended Source': extended_packet_source,
                                  'File': file})

            pcap.close()

            if dict_list:
                output_category_path = os.path.join(topology_path, "Extracted_Dataset")
                os.makedirs(output_category_path, exist_ok=True)

                output_file_path = os.path.join(output_category_path, f'{file.split(".")[0]}_extracted.csv')

                dataFrame = pd.DataFrame(dict_list)
                dataFrame.to_csv(output_file_path, encoding='utf-8', index=False)
                print(f"Saved CSV file to: {output_file_path}")
