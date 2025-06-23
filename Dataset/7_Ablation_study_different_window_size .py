# Ablation study for Type Classification

import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, f1_score
from sklearn.utils.class_weight import compute_class_weight

plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

datasets_info = {
    "topology_A-Duration": {
        "base_path": r".\Merged_Data\6-Merged_sequence_data_fix_durations\Topology_A_fix_duration_",
        "subsets": ["1s", "2s", "3s", "5s"]
    },
    "topology_B-Duration": {
        "base_path": r".\Merged_Data\6-Merged_sequence_data_fix_durations\Topology_B_fix_duration_",
        "subsets": ["1s", "2s", "3s", "5s"]
    },
}
output_folder = "./7-Ablation_CL"
os.makedirs(output_folder, exist_ok=True)

results = []

for dataset_name, info in datasets_info.items():
    base_path = info["base_path"]
    subsets = info["subsets"]

    for subset in subsets:
        file_path = f"{base_path}{subset}.csv"
        experiment_name = f"{dataset_name}_{subset}"
        print(f"\n=== Processing {experiment_name} ===\n")

        try:
            data = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue

        X = data.drop(columns=["Device Name", "Device Type", "File Name"])
        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        X.fillna(X.mean(), inplace=True)
        y = data["Device Type"]

        y = y.astype('category')
        categories = y.cat.categories
        y = y.cat.codes

        print("Category distribution:")
        print(pd.Series(y).value_counts())

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        class_weights = compute_class_weight(class_weight="balanced", classes=pd.Series(y).unique(), y=y)
        class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}

        rf_model = RandomForestClassifier(random_state=42, class_weight=class_weight_dict)
        rf_model.fit(X_train, y_train)

        y_pred = rf_model.predict(X_test)

        actual_categories = sorted(set(y_test) | set(y_pred))
        target_names = [categories[i] for i in actual_categories]

        cm = confusion_matrix(y_test, y_pred, labels=actual_categories)
        report = classification_report(y_test, y_pred, target_names=target_names, labels=actual_categories, zero_division=0)
        print(report)
        savereport_path = os.path.join(output_folder, f"Classification_Report_{experiment_name}.txt")
        with open(savereport_path, "w") as f:
            f.write(report)

        f1_macro = f1_score(y_test, y_pred, average="weighted")
        print(f"Macro F1-Score: {f1_macro:.4f}")

        results.append({
            "Dataset": dataset_name,
            "Window Size": subset,
            "Weighted F1-Score": f1_macro
        })

        plt.figure(figsize=(12, 8))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=target_names, yticklabels=target_names)
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title(f"Confusion Matrix Heatmap - {experiment_name}")
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f"ConfusionMatrix_{experiment_name}.png"))
        plt.close()

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by=["Dataset", "Window Size"])

print("\n=== Weighted F1-Score Comparison Table ===")
print(results_df)

results_df.to_csv(os.path.join(output_folder, "WeightedF1_Comparison.csv"), index=False)

plt.figure(figsize=(14, 8))
sns.barplot(data=results_df, x="Window Size", y="Weighted F1-Score", hue="Dataset")
plt.title("Weighted F1-Score Comparison across Different Window Sizes")
plt.xlabel("Sliding Window Size")
plt.ylabel("Weighted F1-Score")
plt.legend(title="Dataset", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "Weighted F1_Comparison_Barplot_CL.png"))
plt.show()


# Ablation study for Name Classification

import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, f1_score
from sklearn.utils.class_weight import compute_class_weight

plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

def filter_small_classes(data, min_samples=15):
    class_counts = data["Device Name"].value_counts()
    classes_to_keep = class_counts[class_counts >= min_samples].index.tolist()
    filtered_data = data[data["Device Name"].isin(classes_to_keep)].copy()
    return filtered_data

datasets_info = {
    "topology_A-Duration": {
        "base_path": r".\Merged_Data\6-Merged_sequence_data_fix_durations\Topology_A_fix_duration_",
        "subsets": ["1s", "2s", "3s", "5s"]
    },
    "topology_B-Duration": {
        "base_path": r".\Merged_Data\6-Merged_sequence_data_fix_durations\Topology_B_fix_duration_",
        "subsets": ["1s", "2s", "3s", "5s"]
    },
}
output_folder = "./7-Ablation_ID"
os.makedirs(output_folder, exist_ok=True)

results = []

for dataset_name, info in datasets_info.items():
    base_path = info["base_path"]
    subsets = info["subsets"]

    for subset in subsets:
        file_path = f"{base_path}{subset}.csv"
        experiment_name = f"{dataset_name}_{subset}"
        print(f"\n=== Processing {experiment_name} ===\n")

        try:
            data = pd.read_csv(file_path)
            data = filter_small_classes(data, 15)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            continue

        X = data.drop(columns=["Device Name", "Device Type", "File Name"])
        X.replace([np.inf, -np.inf], np.nan, inplace=True)
        X.fillna(X.mean(), inplace=True)
        y = data["Device Name"]

        y = y.astype('category')
        categories = y.cat.categories
        y = y.cat.codes

        print("Category distribution:")
        print(pd.Series(y).value_counts())

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        class_weights = compute_class_weight(class_weight="balanced", classes=pd.Series(y).unique(), y=y)
        class_weight_dict = {i: weight for i, weight in enumerate(class_weights)}

        rf_model = RandomForestClassifier(random_state=42, class_weight=class_weight_dict)
        rf_model.fit(X_train, y_train)

        y_pred = rf_model.predict(X_test)

        actual_categories = sorted(set(y_test) | set(y_pred))
        target_names = [categories[i] for i in actual_categories]

        cm = confusion_matrix(y_test, y_pred, labels=actual_categories)
        report = classification_report(y_test, y_pred, target_names=target_names, labels=actual_categories, zero_division=0)
        print(report)
        savereport_path = os.path.join(output_folder, f"Classification_Report_{experiment_name}.txt")
        with open(savereport_path, "w") as f:
            f.write(report)


        f1_macro = f1_score(y_test, y_pred, average="weighted")
        print(f"Macro F1-Score: {f1_macro:.4f}")

        results.append({
            "Dataset": dataset_name,
            "Window Size": subset,
            "Weighted F1-Score": f1_macro
        })

        plt.figure(figsize=(12, 8))
        sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=target_names, yticklabels=target_names)
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title(f"Confusion Matrix Heatmap - {experiment_name}")
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f"ConfusionMatrix_{experiment_name}.png"))
        plt.close()

results_df = pd.DataFrame(results)
results_df = results_df.sort_values(by=["Dataset", "Window Size"])

print("\n=== Weighted F1-Score Comparison Table ===")
print(results_df)

results_df.to_csv(os.path.join(output_folder, "WeightedF1_Comparison.csv"), index=False)

plt.figure(figsize=(14, 8))
sns.barplot(data=results_df, x="Window Size", y="Weighted F1-Score", hue="Dataset")
plt.title("Weighted F1-Score Comparison across Different Window Sizes")
plt.xlabel("Sliding Window Size")
plt.ylabel("Weighted F1-Score")
plt.legend(title="Dataset", bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(os.path.join(output_folder, "Weighted F1_Comparison_Barplot_ID.png"))
plt.show()
