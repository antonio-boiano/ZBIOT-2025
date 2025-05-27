import os
import pandas as pd
import pyshark

# Define path to tshark executable
tshark_path = r"D:\Wireshark\tshark.exe"

# Device name and type mappings
device_name_mapping_long= {
    "e2:f7:ef:32:aa:9a:c4:74": 'Raspberry 4',
    "0x3c00":'Raspberry 4',
    "16:b9:a9:98:5b:83:06:dc": 'ESP Viola',
    "0xf800": 'ESP Viola',
    "a6:61:97:2d:27:f1:f3:7d": 'ESP Giallo',
    "0x5400": 'ESP Giallo',
    "56:e2:7c:88:8b:3f:94:28": 'ESP Bianco',
    "0x2800":'ESP Bianco',
    "3e:15:d5:65:48:01:fe:56": 'ESP Rosso',
    "0xa000": 'ESP Rosso',
    "ae:9f:d8:a8:7e:a6:4f:ab": 'ESP Azzurro',
    '0xe000':'ESP Azzurro',
    "4a:4b:d9:a6:be:89:7a:3d": 'ESP Arancione',
    '0x9800': 'ESP Arancione',
    "f6:9d:0a:73:00:b9:5e:30": 'Nanoleaf 0176',
    "0xac00": 'Nanoleaf 0176',
    "1e:e4:8d:4c:6e:c8:0c:d3": 'Nanoleaf 1624',
    "0xe400": 'Nanoleaf 1624',
    "da:d5:b2:c1:fb:55:3b:1c": 'Nanoleaf 2248',
    "0x0800": 'Nanoleaf 2248',
    "02:b4:bd:0c:ea:5b:05:2c": 'Onvis',
    "0x8c00": 'Onvis',
    "60:b2:02:04:37:70:02:00": 'Aqara Motion',
    '0xe002': 'Aqara Motion',
    "70:b2:02:04:03:6d:02:00": 'Aqara Door/Window',
    '0xe003': 'Aqara Door/Window',
    "0xffff": "Broadcast"

}

device_type_mapping_long = {
    'e2:f7:ef:32:aa:9a:c4:74': 'OTBR',
    '0x3c00': 'OTBR',
    '16:b9:a9:98:5b:83:06:dc': 'AIRCON',
    '0xf800': 'AIRCON',
    'a6:61:97:2d:27:f1:f3:7d': 'PLUG',
    '0x5400': 'PLUG',
    '56:e2:7c:88:8b:3f:94:28': 'LIGHT',
    '0x2800': 'LIGHT',
    '3e:15:d5:65:48:01:fe:56': 'PLUG',
    '0xa000': 'PLUG',
    'ae:9f:d8:a8:7e:a6:4f:ab': 'LIGHT',
    '0xe000': 'LIGHT',
    '4a:4b:d9:a6:be:89:7a:3d': 'AIRCON',
    '0x9800': 'AIRCON',
    'f6:9d:0a:73:00:b9:5e:30': 'LIGHT',
    '0xac00': 'LIGHT',
    '1e:e4:8d:4c:6e:c8:0c:d3': 'LIGHT',
    '0xe400': 'LIGHT',
    'da:d5:b2:c1:fb:55:3b:1c': 'LIGHT',
    '0x0800': 'LIGHT',
    '02:b4:bd:0c:ea:5b:05:2c': 'PLUG',
    '0x8c00': 'PLUG',
    '60:b2:02:04:37:70:02:00': 'MOTION',
    '0xe002': 'MOTION',
    '70:b2:02:04:03:6d:02:00': 'DOOR',
    '0xe003': 'DOOR',
    "0xffff": "Broadcast"
}


def safe_get_attr(obj, attr, default=None):
    try:
        return getattr(obj, attr, default)
    except:
        return default


def map_device_info(addr, mapping):
    if addr is None:
        return 'Unknown'
    return mapping.get(addr, 'Unknown')


def get_packet_addresses(packet):
    source_addr64 = None
    destination_addr64 = None
    source_addr16 = None
    destination_addr16 = None

    try:
        if hasattr(packet, 'wpan'):
            source_addr64 = safe_get_attr(packet.wpan, 'src64')
            destination_addr64 = safe_get_attr(packet.wpan, 'dst64')
            source_addr16 = safe_get_attr(packet.wpan, 'src16')
            destination_addr16 = safe_get_attr(packet.wpan, 'dst16')
    except:
        pass

    return source_addr64, destination_addr64, source_addr16, destination_addr16


def main(input_file):
    try:
        packets = pyshark.FileCapture(input_file, tshark_path=tshark_path)
    except Exception as e:
        print(f"[ERROR] Failed to open file: {input_file}")
        print(e)
        return pd.DataFrame()

    rows = []
    packet_count = 0

    try:
        for packet in packets:
            packet_count += 1
            try:
                source_addr64, destination_addr64,source_addr16,destination_addr16 = get_packet_addresses(packet)
                source_addr = source_addr64 if source_addr16 is None else source_addr16
                destination_addr = destination_addr64 if destination_addr16 is None else destination_addr16

                device_name = map_device_info(source_addr, device_name_mapping_long)
                device_type = map_device_info(source_addr, device_type_mapping_long)
                device_name_dst = map_device_info(destination_addr, device_name_mapping_long)
                device_type_dst = map_device_info(destination_addr, device_type_mapping_long)

                rows.append({
                    'Packet Number': packet.number,
                    'Device Name': device_name,
                    'Device Type': device_type,
                    'Device Name Destination': device_name_dst,
                    'Device Type Destination': device_type_dst,
                    'Source Address': source_addr if source_addr else '',
                    'Destination Address': destination_addr if destination_addr else '',
                })


            except Exception as e:
                print(f"[WARNING] Error processing packet {packet_count}: {str(e)}")
                rows.append({
                    'Packet Number': packet_count,
                    'Device Name': 'Unknown',
                    'Device Type': 'Unknown',
                    'Device Name Destination': 'Unknown',
                    'Device Type Destination': 'Unknown',
                    'Source Address': '',
                    'Destination Address': '',
                })
                continue

    except Exception as e:
        print(f"[ERROR] Error during packet iteration: {str(e)}")
    finally:
        packets.close()

    print(f"[INFO] Total processed: {packet_count} packets")
    print(f"[INFO] Successfully extracted: {len(rows)} records from {input_file}")

    return pd.DataFrame(rows)


def find_and_process_pcapng(file_path):
    for root, dirs, files in os.walk(file_path):
        for file in files:
            if file.endswith('.pcapng'):
                full_path = os.path.join(root, file)
                groundtruth_folder = os.path.join(root, "1-Groundtruth")
                os.makedirs(groundtruth_folder, exist_ok=True)
                output_file = os.path.join(groundtruth_folder, os.path.splitext(file)[0] + '_groundtruth.csv')

                print(f"Processing: {full_path} -> {output_file}")
                groundtruth = main(full_path)

                groundtruth.to_csv(output_file, index=False)
                print(f"[SUCCESS] Saved {len(groundtruth)} records to {output_file}")


    print("All files processed successfully.")

if __name__ == "__main__":
    root_path = r"D:\ZBIOT-2025\Dataset\Long captures"
    find_and_process_pcapng(root_path)