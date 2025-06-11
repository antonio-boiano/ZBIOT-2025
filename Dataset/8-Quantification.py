import pandas as pd
import os
import numpy as np
def quantize(data, b):
    min_val = data.min()
    max_val = np.percentile(data, 99.9)

    levels = 2 ** b
    step = (max_val - min_val) / levels

    quantized_indexes = np.floor((data - min_val) / step)
    quantized_indexes = np.clip(quantized_indexes, 0, levels - 1)
    quantized_data = quantized_indexes * step + min_val + step / 2

    return quantized_data, quantized_indexes

base_dir = "D:/ZBIOT-2025/Dataset"
input_folder = os.path.join(base_dir, "Merged_Data", "A_6-Merged_sequence_data_fix_durations")
output_folder = os.path.join(base_dir, "Quantized_Data", "A_6-Merged_sequence_data_fix_durations", "Quantized_values")
output_folder2 = os.path.join(base_dir, "Quantized_Data", "A_6-Merged_sequence_data_fix_durations", "Quantized_index")
os.makedirs(output_folder, exist_ok=True)
os.makedirs(output_folder2, exist_ok=True)

b_values = list(range(1, 33))

file_name = "Topology_A_fix_duration_5s.csv"
input_file_path = os.path.join(input_folder, file_name)
df = pd.read_csv(input_file_path)
columns_to_quantize = df.columns[3:]

for b in b_values:
    try:
        quantized_df = df.copy()
        index_df = df.copy()
        for col in columns_to_quantize:
            quantized_values, quantized_indexes = quantize(df[col].values, b)
            quantized_df[col] = quantized_values
            index_df[col] = quantized_indexes

        new_file_name = file_name.replace(".csv", "")
        output_file = os.path.join(output_folder, f"{new_file_name}_value_b{b}.csv")
        output_index_file = os.path.join(output_folder2, f"{new_file_name}_index_b{b}.csv")

        quantized_df.to_csv(output_file, index=False)
        index_df.to_csv(output_index_file, index=False)
    except MemoryError:
        print(f"Quantization failed for b={b}")

file_paths = {f"b{b}": os.path.join(output_folder, f"{new_file_name}_value_b{b}.csv") for b in b_values}
file_paths["Original"] = os.path.join(input_folder, file_name)
