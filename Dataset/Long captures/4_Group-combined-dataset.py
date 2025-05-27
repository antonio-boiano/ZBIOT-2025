import os

dataset_dir = "D:\ZBIOT-2025\Dataset"
import pandas as pd

def group_by_each_device(data):
    result_data = []

    unique_devices = pd.unique(data[['Device Name', 'Device Name Destination']].values.ravel('K'))
    for device in unique_devices:
        # Filter out rows related to the current device
        related_rows = (data['Device Name'] == device) | (data['Device Name Destination'] == device)
        group_data = data[related_rows].copy()

        # Add group name column (first column)
        group_data.insert(0, 'Group', f"{device}")

        # Dynamically generate Group Type columns
        if 'Group Type' in group_data.columns:
            group_data.drop(columns=['Group Type'], inplace=True)

        group_data['Group Type'] = None
        group_data.loc[group_data['Device Name'] == device, 'Group Type'] = group_data['Device Type']
        group_data.loc[group_data['Device Name Destination'] == device, 'Group Type'] = group_data[
            'Device Type Destination']

        group_data.insert(1, 'Group Type', group_data.pop('Group Type'))
        # group_data = group_data[
        #     (group_data['Device Name ZigBee'] == device) | (group_data['Device Name ZigBee Destination'] == device)]
        result_data.append(group_data)

    result_data = pd.concat(result_data, ignore_index=True)
    return result_data

long_path = os.path.join(dataset_dir, "Long captures")

raw_data_path = os.path.join(long_path, "3-Combined_dataset")
group_data_path = os.path.join(long_path, "A_4-Group_dataset")
os.makedirs(raw_data_path, exist_ok=True)
os.makedirs(group_data_path, exist_ok=True)

for file in os.listdir(raw_data_path):
    if file.endswith('_combined.csv'):
        try:
            base_name = file.replace('_combined.csv', '')
            input_file_path = os.path.join(raw_data_path, file)
            output_file_path = os.path.join(group_data_path, f"{base_name}_group.csv")

            raw_data = pd.read_csv(input_file_path)
            grouped_data = group_by_each_device(raw_data)
            grouped_data.to_csv(output_file_path, index=False)

            print(f"Successfully processed and saved {output_file_path}")

        except Exception as e:
            print(f"Error processing file {file}: {e}")
