# import pandas as pd
# import os
# import numpy as np
#
#
#
# def quantize(data, b):
#     min_val = data.min()
#     max_val = data.max()
#
#     levels = 2 ** b
#     step = (max_val - min_val) / levels
#
#     quantized_indexes = np.floor((data - min_val) / step)
#
#     quantized_indexes = np.clip(quantized_indexes, 0, levels - 1)
#
#     quantized_data = quantized_indexes * step + min_val
#
#     return quantized_data, quantized_indexes
#
#
# base_dir = os.path.dirname(os.path.abspath(__file__))
#
# input_folders = [
#     os.path.join(base_dir, "Merged_Data", "A_6-Merged_sequence_data_fix_durations"),
#     os.path.join(base_dir, "Merged_Data", "A_6-Merged_sequence_data_fix_packets"),
# ]
#
# output_base_folder = os.path.join(base_dir, "Quantized_Data")
#
# b_values = [2, 4, 8, 16, 32]
#
# for input_folder in input_folders:
#     relative_path = os.path.relpath(input_folder, os.path.join(base_dir, "Merged_Data"))
#     output_folder = os.path.join(output_base_folder, relative_path)
#
#     quantized_values_folder = os.path.join(output_folder, "Quantized_values")
#     quantized_intervals_folder = os.path.join(output_folder, "Quantized_index")
#     os.makedirs(quantized_values_folder, exist_ok=True)
#     os.makedirs(quantized_intervals_folder, exist_ok=True)
#
#     for file_name in os.listdir(input_folder):
#         if file_name.endswith(".csv"):
#             input_file_path = os.path.join(input_folder, file_name)
#             df = pd.read_csv(input_file_path)
#
#             columns_to_quantize = df.columns[3:10]
#
#             for b in b_values:
#                 try:
#                     quantized_df = df.copy()
#                     quantized_index_df = df.copy()
#
#                     for col in columns_to_quantize:
#                         quantized_values, quantized_indexes = quantize(df[col].values, b)
#                         quantized_df[col] = quantized_values
#                         quantized_index_df[col] = quantized_indexes
#
#                     quantized_value_file = os.path.join(quantized_values_folder, f"{file_name}_value_b{b}.csv")
#                     quantized_index_file = os.path.join(quantized_intervals_folder, f"{file_name}_index_b{b}.csv")
#
#                     quantized_df.to_csv(quantized_value_file, index=False)
#                     quantized_index_df.to_csv(quantized_index_file, index=False)
#
#                 except MemoryError:
#                     print(f"Quantification of failure")

import pandas as pd
import os
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import accuracy_score
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt

def quantize(data, b):
    min_val = data.min()
    max_val = data.max()

    levels = 2 ** b
    step = (max_val - min_val) / levels

    quantized_indexes = np.floor((data - min_val) / step)
    quantized_indexes = np.clip(quantized_indexes, 0, levels - 1)

    quantized_data = quantized_indexes * step + min_val
    return quantized_data, quantized_indexes

base_dir = "D:/ZBIOT-2025/Dataset"
input_folder = os.path.join(base_dir, "Merged_Data", "A_6-Merged_sequence_data_fix_durations")
output_folder = os.path.join(base_dir, "Quantized_Data", "A_6-Merged_sequence_data_fix_durations", "Quantized_values")
output_folder2 = os.path.join(base_dir, "Quantized_Data", "A_6-Merged_sequence_data_fix_durations", "Quantized_index")
os.makedirs(output_folder, exist_ok=True)

b_values = list(range(1, 33))  # 让 b 从 1 到 32

file_name = "Topology_B_fix_duration.csv"
input_file_path = os.path.join(input_folder, file_name)
df = pd.read_csv(input_file_path)
columns_to_quantize = df.columns[3:10]

for b in b_values:
    try:
        quantized_df = df.copy()
        for col in columns_to_quantize:
            quantized_values, _ = quantize(df[col].values, b)
            quantized_df[col] = quantized_values

        output_file = os.path.join(output_folder, f"{file_name}_value_b{b}.csv")
        quantized_df.to_csv(output_file, index=False)
    except MemoryError:
        print(f"Quantization failed for b={b}")

file_paths = {f"b{b}": os.path.join(output_folder, f"{file_name}_value_b{b}.csv") for b in b_values}
file_paths["Original"] = os.path.join(input_folder, file_name)

folds = 5
accuracies_per_file = {file_name: [] for file_name in file_paths.keys() if file_name != "Original"}

original_data = pd.read_csv(file_paths["Original"])
X_original = original_data.drop(columns=["Device Name", "Device Type", "File Name"])
y_original = original_data["Device Type"]
y_original = y_original.astype("category")
categories = y_original.cat.categories
y_original = y_original.cat.codes

skf = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)

for train_indices, test_indices in skf.split(X_original, y_original):
    X_train, X_test = X_original.iloc[train_indices], X_original.iloc[test_indices]
    y_train, y_test_original = y_original[train_indices], y_original[test_indices]
    class_weights = compute_class_weight(class_weight="balanced", classes=np.unique(y_train), y=y_train)
    class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}
    rf_model = RandomForestClassifier(random_state=42, class_weight=class_weight_dict)
    rf_model.fit(X_train, y_train)
    for file_name, file_path in file_paths.items():
        if file_name == "Original":
            continue

        quantized_data = pd.read_csv(file_path)
        X_test_quantized = quantized_data.drop(columns=["Device Name", "Device Type", "File Name"]).iloc[test_indices]
        y_test_quantized = quantized_data["Device Type"].iloc[test_indices]
        y_test_quantized = y_test_quantized.astype("category")
        y_test_quantized = y_test_quantized.cat.set_categories(categories).cat.codes

        y_pred = rf_model.predict(X_test_quantized)
        acc = accuracy_score(y_test_quantized, y_pred)
        accuracies_per_file[file_name].append(acc)

mean_accuracies = {file_name: np.mean(accs) for file_name, accs in accuracies_per_file.items()}
std_accuracies = {file_name: np.std(accs) for file_name, accs in accuracies_per_file.items()}

print("\n=== Final Results ===")
for file_name, mean_acc in sorted(mean_accuracies.items(), key=lambda x: int(x[0][1:])):
    print(f"{file_name}: Mean Accuracy = {mean_acc:.4f}, Std = {std_accuracies[file_name]:.4f}")

plt.figure(figsize=(10, 6))
b_values_sorted = sorted(mean_accuracies.keys(), key=lambda x: int(x[1:]))
plt.errorbar(
    b_values_sorted,
    [mean_accuracies[b] for b in b_values_sorted],
    yerr=[std_accuracies[b] for b in b_values_sorted],
    fmt="o-", capsize=5, label="Accuracy with Error Bars", color="blue",
)
plt.title("Accuracy Comparison Across Quantization Levels (b=1 to 32)", fontsize=16)
plt.xlabel("Quantization Level (b)", fontsize=14)
plt.ylabel("Accuracy", fontsize=14)
plt.ylim(0.4, 0.9)
plt.xticks(rotation=90)
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend(fontsize=12)
plt.show()
