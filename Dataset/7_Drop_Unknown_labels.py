import os
import pandas as pd

sequence_data_dir = "./Data/Sequence_Data"

for file in os.listdir(sequence_data_dir):
    if file.endswith(".csv"):
        file_path = os.path.join(sequence_data_dir, file)
        df = pd.read_csv(file_path)
        df = df.dropna(axis=0, how="any")
        df = df[df["Device Name"] != "Unknown"]
        new_file_name = f"{os.path.splitext(file)[0]}_known.csv"
        new_file_path = os.path.join(sequence_data_dir, new_file_name)
        df.to_csv(new_file_path, index=False)

