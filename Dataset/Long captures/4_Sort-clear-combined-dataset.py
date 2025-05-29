import os
import pandas as pd

long_path = "."

topology_path = os.path.join(long_path, "3-Combined_dataset")
saveto_path = os.path.join(long_path, "4-Sort_dataset")
os.makedirs(saveto_path, exist_ok=True)

for file in os.listdir(topology_path):
    file_path = os.path.join(topology_path, file)
    if not file.endswith(".csv"):
        continue

    try:
        df = pd.read_csv(file_path)

        missing_cols = [col for col in ["Device Name", "Time"] if col not in df.columns]
        if missing_cols:
            print(f"Missing columns {missing_cols} in file: {file_path}")
            continue

        sorted_df = df.sort_values(by=["Device Name", "Time"], ascending=[True, True])

        base_name = file.replace('_combined.csv', '_sort.csv')
        output_file_path = os.path.join(saveto_path, base_name)

        sorted_df.to_csv(output_file_path, index=False, encoding="utf-8")

        print(f"Sorted file saved successfully: {output_file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
