import pandas as pd
import os
import numpy as np
import math
import pyarrow as pa
import pyarrow.parquet as pq

def quantize(data, b):
    min_val = data.min()
    max_val = np.percentile(data, 99.9)

    levels = 2 ** b
    step = (max_val - min_val) / levels

    quantized_indexes = np.floor((data - min_val) / step)
    quantized_indexes = np.clip(quantized_indexes, 0, levels - 1)
    quantized_data = quantized_indexes * step + min_val + step / 2

    return quantized_data, quantized_indexes

def pack_bits(data, bit_width):
    """Pack integer values into a byte array using exactly bit_width bits per value."""
    data = np.array(data, dtype=np.uint64).flatten()
    n = len(data)
    total_bits = n * bit_width
    total_bytes = math.ceil(total_bits / 8)
    
    result = np.zeros(total_bytes, dtype=np.uint8)
    
    bit_pos = 0
    for val in data:
        for b in range(bit_width):
            if val & (1 << b):
                byte_idx = bit_pos // 8
                bit_idx = bit_pos % 8
                result[byte_idx] |= (1 << bit_idx)
            bit_pos += 1
    
    return result

def get_optimal_dtype(bit_width):
    """Return the smallest numpy dtype that can hold the given bit width."""
    if bit_width <= 8:
        return np.uint8
    elif bit_width <= 16:
        return np.uint16
    elif bit_width <= 32:
        return np.uint32
    else:
        return np.uint64

def get_pyarrow_type(bit_width):
    """Return the smallest PyArrow type that can hold the given bit width."""
    if bit_width <= 8:
        return pa.uint8()
    elif bit_width <= 16:
        return pa.uint16()
    elif bit_width <= 32:
        return pa.uint32()
    else:
        return pa.uint64()

def create_device_mapping(device_names):
    """Create a mapping from device names to 16-bit identifiers."""
    unique_devices = device_names.unique()
    return {name: idx for idx, name in enumerate(unique_devices)}

def save_device_mapping(mapping, output_path):
    """Save device name to ID mapping for reference."""
    mapping_df = pd.DataFrame(list(mapping.items()), columns=['Device_Name', 'Device_ID'])
    mapping_df.to_csv(output_path, index=False)

def save_parquet_with_proper_types(df, output_path, bit_width, compression=None):
    """Save dataframe to parquet with proper data types based on bit width."""
    # Build PyArrow schema with correct types
    fields = [('Device_ID', pa.uint16())]
    data_type = get_pyarrow_type(bit_width)
    
    for col in df.columns[1:]:  # Skip Device_ID
        fields.append((col, data_type))
    
    schema = pa.schema(fields)
    
    # Convert dataframe to PyArrow table with explicit schema
    table = pa.Table.from_pandas(df, schema=schema, preserve_index=False)
    
    # Write parquet with specified compression
    pq.write_table(
        table, 
        output_path, 
        compression=compression,
        use_dictionary=False,
        write_statistics=False
    )

# Parquet compression options
PARQUET_COMPRESSIONS = [
    None,       # UNCOMPRESSED
    'snappy',
    'gzip',
    'brotli',
    'zstd',
    'lz4',
]

input_folder = os.path.join("./Dataset/6-Merged_Data", "6-Merged_sequence_data_fix_durations")

# Output folders
output_folder_values = os.path.join("./Dataset/8-Quantized_Data", "Quantized_values")
output_folder_index_csv = os.path.join("./Dataset/8-Quantized_Data", "Quantized_index_csv")
output_folder_index_parquet = os.path.join("./Dataset/8-Quantized_Data", "Quantized_index_parquet")
output_folder_index_bitpacked = os.path.join("./Dataset/8-Quantized_Data", "Quantized_index_bitpacked")
output_folder_index_npy = os.path.join("./Dataset/8-Quantized_Data", "Quantized_index_npy")


os.makedirs(output_folder_values, exist_ok=True)
os.makedirs(output_folder_index_csv, exist_ok=True)
os.makedirs(output_folder_index_parquet, exist_ok=True)
os.makedirs(output_folder_index_bitpacked, exist_ok=True)
os.makedirs(output_folder_index_npy, exist_ok=True)

# Create subfolders for each parquet compression type
for comp in PARQUET_COMPRESSIONS:
    comp_name = comp if comp else 'uncompressed'
    os.makedirs(os.path.join(output_folder_index_parquet, comp_name), exist_ok=True)

# Bit values: 1-16 plus 32, 64
b_values = list(range(1, 65))

file_name = "Topology_A_fix_duration_5s.csv"
input_file_path = os.path.join(input_folder, file_name)
df = pd.read_csv(input_file_path)

# Create device name mapping (from first 3 columns, assuming 'Device Name' is one of them)
device_column = df.columns[0]  # Assuming device name is first column
device_mapping = create_device_mapping(df[device_column])
save_device_mapping(device_mapping, os.path.join("8-Quantized_Data", "device_mapping.csv"))

# Create device IDs as 16-bit identifiers
device_ids = df[device_column].map(device_mapping).values.astype(np.uint16)

columns_to_quantize = df.columns[3:]
base_file_name = file_name.replace(".csv", "")

for b in b_values:
    try:
        print(f"Processing b={b}...")
        
        quantized_df = df.copy()
        index_df = df.copy()
        
        for col in columns_to_quantize:
            quantized_values, quantized_indexes = quantize(df[col].values, b)
            quantized_df[col] = quantized_values
            index_df[col] = quantized_indexes

        # === Save quantized VALUES as CSV (keep all columns) ===
        output_file_values = os.path.join(output_folder_values, f"{base_file_name}_value_b{b}.csv")
        quantized_df.to_csv(output_file_values, index=False)

        # === Prepare index dataframe: remove first 3 columns, add device ID ===
        index_df_processed = index_df.iloc[:, 3:].copy()  # Remove first 3 columns
        index_df_processed.insert(0, 'Device_ID', device_ids)  # Add 16-bit device ID
        
        # Convert to optimal dtype for the bit width
        optimal_dtype = get_optimal_dtype(b)
        for col in index_df_processed.columns[1:]:  # Skip Device_ID column
            index_df_processed[col] = index_df_processed[col].astype(optimal_dtype)
        
        # Ensure Device_ID is uint16
        index_df_processed['Device_ID'] = index_df_processed['Device_ID'].astype(np.uint16)

        # === Save INDEX as CSV ===
        output_index_csv = os.path.join(output_folder_index_csv, f"{base_file_name}_index_b{b}.csv")
        index_df_processed.to_csv(output_index_csv, index=False)

        # === Save INDEX as Parquet with all compression options ===
        for comp in PARQUET_COMPRESSIONS:
            comp_name = comp if comp else 'uncompressed'
            output_index_parquet = os.path.join(
                output_folder_index_parquet, 
                comp_name, 
                f"{base_file_name}_index_b{b}.parquet"
            )
            save_parquet_with_proper_types(
                index_df_processed,
                output_index_parquet,
                b,
                compression=comp
            )

        # === Save INDEX as NPY (numpy binary format) ===
        output_index_npy = os.path.join(
            output_folder_index_npy, 
            f"{base_file_name}_index_b{b}.npy"
        )
        # Convert to numpy array with optimal dtype
        # Store Device_ID separately since it's always uint16
        npy_data = index_df_processed.iloc[:, 1:].values.astype(optimal_dtype)  # Data columns
        npy_device_ids = index_df_processed['Device_ID'].values.astype(np.uint16)
        
        # Save as structured array to preserve both
        structured_dtype = np.dtype([
            ('device_id', np.uint16),
            ('data', optimal_dtype, (npy_data.shape[1],))
        ])
        structured_array = np.zeros(len(npy_data), dtype=structured_dtype)
        structured_array['device_id'] = npy_device_ids
        structured_array['data'] = npy_data
        np.save(output_index_npy, structured_array)

        # === Save INDEX as custom bit-packed binary format ===
        output_index_bitpacked = os.path.join(
            output_folder_index_bitpacked, 
            f"{base_file_name}_index_b{b}.bin"
        )
        
        # Pack all data: Device_ID (16 bits) + quantized columns (b bits each)
        with open(output_index_bitpacked, 'wb') as f:
            # Write header: number of rows, number of data columns, bit width
            n_rows = len(index_df_processed)
            n_data_cols = len(index_df_processed.columns) - 1  # Exclude Device_ID
            header = np.array([n_rows, n_data_cols, b], dtype=np.uint32)
            header.tofile(f)
            
            # Write device IDs (16-bit each)
            index_df_processed['Device_ID'].values.astype(np.uint16).tofile(f)
            
            # Pack and write each quantized column with exact bit width
            for col in index_df_processed.columns[1:]:  # Skip Device_ID
                packed_col = pack_bits(index_df_processed[col].values.astype(np.uint64), b)
                packed_col.tofile(f)
        
        print(f"  Completed b={b}")
        
    except MemoryError:
        print(f"Quantization failed for b={b} due to MemoryError")
    except Exception as e:
        print(f"Quantization failed for b={b}: {e}")

# Summary of file paths
print("\n=== Output Summary ===")
print(f"Quantized values (CSV): {output_folder_values}")
print(f"Quantized index (CSV): {output_folder_index_csv}")
print(f"Quantized index (Parquet): {output_folder_index_parquet}")
print(f"  Compressions: {[c if c else 'uncompressed' for c in PARQUET_COMPRESSIONS]}")
print(f"Quantized index (NPY): {output_folder_index_npy}")
print(f"Quantized index (Bit-packed): {output_folder_index_bitpacked}")
print(f"Device mapping: 8-Quantized_Data/device_mapping.csv")
print(f"\nBit widths processed: {b_values}")
print(f"Data types used:")
print(f"  1-8 bits:   uint8")
print(f"  9-16 bits:  uint16")
print(f"  17-32 bits: uint32")
print(f"  33-64 bits: uint64")

file_paths = {f"b{b}": os.path.join(output_folder_values, f"{base_file_name}_value_b{b}.csv") for b in b_values}
file_paths["Original"] = os.path.join(input_folder, file_name)