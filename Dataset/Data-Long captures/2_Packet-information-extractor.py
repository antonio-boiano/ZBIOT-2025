import os
import subprocess
import pandas as pd

# Define path to tshark executable (should be in $PATH)
tshark_path = "tshark"

long_path = "."


for file in os.listdir(long_path):
    file_path = os.path.join(long_path, file)

    if not os.path.isfile(file_path) or not file.endswith('.pcapng'):
        continue

    print(f"Processing file: {file}")

    output_category_path = os.path.join(long_path, "2-Information_From_PCAP")
    os.makedirs(output_category_path, exist_ok=True)
    output_file_path = os.path.join(output_category_path, file.split(".")[0] + "_keyinformation.csv")

    try:
        tshark_command = [
            tshark_path,
            "-r", file_path,
            "-T", "fields",  # Output field format
            "-e", "frame.time",  # time field
            "-e", "frame.time_delta_displayed",  # timing difference
            "-e", "frame.len",  # Frame Length field
            "-e", "wpan.src16",  # IEEE Source Address Field
            "-e", "wpan.dst16",  # IEEE Destination Address Field
            "-e", "wpan.src64",  # IEEE Source Address Field (64-bit)
            "-e", "wpan.dst64",  # IEEE Destination Address Field (64-bit)
            "-e", "wpan.seq_no",  # Serial number field
            "-e", "wpan.fcf", # Frame Control Field
            "-e", "wpan.fcs",  # Frame Check Sequence
            "-E", "header=y",  # The output file contains the header
            "-E", "separator=,",  # Field separators are commas
            "-E", "quote=d",  # double quote
            "-E", "occurrence=f"  # Only one occurrence of field data for each record
        ]

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            subprocess.run(tshark_command, stdout=output_file, check=True)

        print(f"Saved CSV file to: {output_file_path}")

        df = pd.read_csv(output_file_path)

        df[df.columns[0]] = df[df.columns[0]].str.replace(
            " ora legale Europa occidentale", "", regex=True
        )

        df['frame.time'] = pd.to_datetime(df['frame.time'])
        df['time_diff_seconds'] = df['frame.time'].diff(1).apply(lambda x: x.total_seconds() if not pd.isna(x) else 0)

        df = df.drop(columns=['frame.time_delta_displayed'])

        new_headers = {
            "frame.time": "Time",
            "time_diff_seconds": "Delta Time",
            "frame.len": "Length",
            "wpan.src16": "Source IEEE",
            "wpan.dst16": "Destination IEEE",
            "wpan.src64": "Source IEEE 64-bit",
            "wpan.dst64": "Destination IEEE 64-bit",
            "wpan.seq_no": "Sequence Number",
            "wpan.fcf": "Frame Control Field",
            "wpan.fcs": "Frame Check Sequence",
        }

        df.rename(columns=new_headers, inplace=True)
        df.to_csv(output_file_path, index=False, encoding='utf-8')
        print(f"Renamed headers and saved CSV file to: {output_file_path}")

        df = pd.read_csv(output_file_path)
        # Removal of redundant notes in the time format. The time of different country versions is not the same, pay attention to change

        df.to_csv(output_file_path, index=False, encoding='utf-8')
        print(f"Cleaned and saved CSV file to: {output_file_path}")
    except subprocess.CalledProcessError as e:

        print(f"Failed to process file: {file}\nError: {e}")

    except Exception as e:
        print(f"An error occurred while processing: {file}\nError: {e}")

