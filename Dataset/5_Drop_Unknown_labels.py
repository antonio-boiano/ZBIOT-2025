import os
import pandas as pd

aggregated_data_dir = "./Data/Aggregated_Data"

for file in os.listdir(aggregated_data_dir):
    if file.endswith(".csv"):
        file_path = os.path.join(aggregated_data_dir, file)
        df = pd.read_csv(file_path)
        df = df.dropna(subset=["Delta Time"])
        df = df[df["Device Name"] != "Unknown"]
        new_file_name = f"{os.path.splitext(file)[0]}_known.csv"
        new_file_path = os.path.join(aggregated_data_dir, new_file_name)
        df.to_csv(new_file_path, index=False)
