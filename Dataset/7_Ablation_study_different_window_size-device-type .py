import pandas as pd
import numpy as np
import os
import seaborn as sns
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import confusion_matrix, classification_report, f1_score, accuracy_score
from sklearn.utils.class_weight import compute_class_weight


def run_xgboost_classification(task_name, file_path, output_folder, hyperparameters):
    """
    Execute XGBoost classification with 5-fold cross-validation.
    
    Parameters:
    -----------
    task_name : str
        Identifier for the experimental task (used in output filenames)
    file_path : str
        Path to the input CSV dataset
    output_folder : str
        Directory path for saving outputs
    hyperparameters : dict
        XGBoost hyperparameter configuration
    
    Returns:
    --------
    dict
        Dictionary containing aggregated performance metrics
    """
    
    print(f"\n{'='*80}")
    print(f"PROCESSING TASK: {task_name}")
    print(f"{'='*80}\n")
    
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)
    
    # Load dataset
    try:
        data = pd.read_csv(file_path)
        print(f"Dataset loaded successfully: {file_path}")
        print(f"Dataset shape: {data.shape}\n")
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        return None
    
    # Feature engineering: prepare features and target
    X = data.drop(columns=["Device Name", "Device Type", "File Name"])
    X.replace([np.inf, -np.inf], np.nan, inplace=True)
    X.fillna(X.mean(), inplace=True)
    y = data["Device Type"]
    
    # Category encoding
    y = y.astype('category')
    categories = y.cat.categories
    y_encoded = y.cat.codes
    
    print("Category Distribution:")
    print(y.value_counts())
    print()
    
    # Initialize stratified k-fold cross-validation
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Metric storage arrays
    accuracy_scores = []
    f1_macro_scores = []
    f1_weighted_scores = []
    precision_scores = []
    recall_scores = []
    
    # Storage for confusion matrices and predictions
    all_confusion_matrices = []
    all_y_test = []
    all_y_pred = []
    
    print(f"{'='*80}")
    print("5-FOLD CROSS-VALIDATION - XGBoost Classifier")
    print(f"{'='*80}")
    print(f"Hyperparameters: {hyperparameters}\n")
    
    # Cross-validation loop
    for fold, (train_idx, test_idx) in enumerate(skf.split(X, y_encoded), 1):
        print(f"Fold {fold}/5:")
        print("-" * 40)
        
        # Data partitioning
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y_encoded.iloc[train_idx], y_encoded.iloc[test_idx]
        
        # Compute class weights for handling imbalanced datasets
        class_weights = compute_class_weight(
            class_weight="balanced", 
            classes=np.unique(y_train), 
            y=y_train
        )
        
        # Convert to sample weights (XGBoost-compatible format)
        sample_weights = np.array([class_weights[i] for i in y_train])
        
        # Initialize XGBoost classifier with specified hyperparameters
        xgb_model = XGBClassifier(
            random_state=42,
            eval_metric='mlogloss',
            use_label_encoder=False,
            **hyperparameters
        )
        
        # Model training
        xgb_model.fit(X_train, y_train, sample_weight=sample_weights)
        
        # Prediction
        y_pred = xgb_model.predict(X_test)
        
        # Metric computation
        accuracy = accuracy_score(y_test, y_pred)
        f1_macro = f1_score(y_test, y_pred, average="macro", zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average="weighted", zero_division=0)
        
        # Extract precision and recall from classification report
        report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
        precision = report['macro avg']['precision']
        recall = report['macro avg']['recall']
        
        # Store fold-level metrics
        accuracy_scores.append(accuracy)
        f1_macro_scores.append(f1_macro)
        f1_weighted_scores.append(f1_weighted)
        precision_scores.append(precision)
        recall_scores.append(recall)
        
        # Generate confusion matrix
        cm = confusion_matrix(y_test, y_pred, labels=range(len(categories)))
        all_confusion_matrices.append(cm)
        
        # Aggregate predictions across folds
        all_y_test.extend(y_test)
        all_y_pred.extend(y_pred)
        
        # Display fold-level performance
        print(f"  Accuracy:        {accuracy:.4f}")
        print(f"  Precision (avg): {precision:.4f}")
        print(f"  Recall (avg):    {recall:.4f}")
        print(f"  F1-Macro:        {f1_macro:.4f}")
        print(f"  F1-Weighted:     {f1_weighted:.4f}\n")
    
    # Calculate summary statistics
    print(f"{'='*80}")
    print("CROSS-VALIDATION SUMMARY (mean ± std)")
    print(f"{'='*80}")
    print(f"Accuracy:        {np.mean(accuracy_scores):.4f} ± {np.std(accuracy_scores):.4f}")
    print(f"Precision (avg): {np.mean(precision_scores):.4f} ± {np.std(precision_scores):.4f}")
    print(f"Recall (avg):    {np.mean(recall_scores):.4f} ± {np.std(recall_scores):.4f}")
    print(f"F1-Macro:        {np.mean(f1_macro_scores):.4f} ± {np.std(f1_macro_scores):.4f}")
    print(f"F1-Weighted:     {np.mean(f1_weighted_scores):.4f} ± {np.std(f1_weighted_scores):.4f}")
    print(f"{'='*80}\n")
    
    # Generate comprehensive classification report
    all_y_test = np.array(all_y_test)
    all_y_pred = np.array(all_y_pred)
    
    merged_report = classification_report(
        all_y_test, 
        all_y_pred, 
        target_names=categories, 
        labels=range(len(categories)),
        zero_division=0
    )
    
    print(f"{'='*80}")
    print("MERGED CLASSIFICATION REPORT (All Folds Combined)")
    print(f"{'='*80}")
    print(merged_report)
    print(f"{'='*80}\n")
    
    # Save classification report
    report_path = os.path.join(output_folder, f"Classification_Report_{task_name}.txt")
    with open(report_path, "w") as f:
        f.write(f"Task: {task_name}\n")
        f.write(f"Hyperparameters: {hyperparameters}\n\n")
        f.write("="*80 + "\n")
        f.write("CROSS-VALIDATION SUMMARY\n")
        f.write("="*80 + "\n")
        f.write(f"Accuracy:        {np.mean(accuracy_scores):.4f} ± {np.std(accuracy_scores):.4f}\n")
        f.write(f"Precision (avg): {np.mean(precision_scores):.4f} ± {np.std(precision_scores):.4f}\n")
        f.write(f"Recall (avg):    {np.mean(recall_scores):.4f} ± {np.std(recall_scores):.4f}\n")
        f.write(f"F1-Macro:        {np.mean(f1_macro_scores):.4f} ± {np.std(f1_macro_scores):.4f}\n")
        f.write(f"F1-Weighted:     {np.mean(f1_weighted_scores):.4f} ± {np.std(f1_weighted_scores):.4f}\n\n")
        f.write("="*80 + "\n")
        f.write("MERGED CLASSIFICATION REPORT\n")
        f.write("="*80 + "\n")
        f.write(merged_report)
    
    print(f"Classification report saved: {report_path}")
    
    # Aggregate confusion matrices
    summed_cm = np.sum(all_confusion_matrices, axis=0)
    relative_cm = summed_cm.astype('float') / summed_cm.sum(axis=1)[:, np.newaxis]
    
    # Visualization 1: Absolute confusion matrix
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        summed_cm, 
        annot=True, 
        fmt="d", 
        cmap="Blues", 
        xticklabels=categories, 
        yticklabels=categories, 
        annot_kws={"size": 16}
    )
    plt.xlabel("Predicted Label", fontsize=18)
    plt.ylabel("True Label", fontsize=18)
    plt.title(f"Confusion Matrix - {task_name}\n(Absolute Counts, Summed Over 5 Folds)", fontsize=20)
    plt.xticks(fontsize=14, rotation=45, ha='right')
    plt.yticks(fontsize=14, rotation=0)
    plt.tight_layout()
    absolute_cm_path = os.path.join(output_folder, f"ConfusionMatrix_Absolute_{task_name}.png")
    plt.savefig(absolute_cm_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Absolute confusion matrix saved: {absolute_cm_path}")
    
    # Visualization 2: Normalized confusion matrix
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        relative_cm, 
        annot=True, 
        fmt=".2f", 
        cmap="Blues", 
        xticklabels=categories, 
        yticklabels=categories, 
        annot_kws={"size": 16},
        vmin=0,
        vmax=1
    )
    plt.xlabel("Predicted Label", fontsize=18)
    plt.ylabel("True Label", fontsize=18)
    plt.title(f"Confusion Matrix - {task_name}\n(Normalized by True Label)", fontsize=20)
    plt.xticks(fontsize=14, rotation=45, ha='right')
    plt.yticks(fontsize=14, rotation=0)
    plt.tight_layout()
    relative_cm_path = os.path.join(output_folder, f"ConfusionMatrix_Normalized_{task_name}.png")
    plt.savefig(relative_cm_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Normalized confusion matrix saved: {relative_cm_path}\n")
    
    # Return aggregated metrics
    return {
        "Task": task_name,
        "Accuracy": np.mean(accuracy_scores),
        "Accuracy_std": np.std(accuracy_scores),
        "Precision": np.mean(precision_scores),
        "Precision_std": np.std(precision_scores),
        "Recall": np.mean(recall_scores),
        "Recall_std": np.std(recall_scores),
        "F1-Macro": np.mean(f1_macro_scores),
        "F1-Macro_std": np.std(f1_macro_scores),
        "F1-Weighted": np.mean(f1_weighted_scores),
        "F1-Weighted_std": np.std(f1_weighted_scores)
    }


# Main execution block
if __name__ == "__main__":
    
    # Define hyperparameters
    xgb_hyperparameters = {
        'colsample_bytree': 0.4,
        'gamma': 0,
        'learning_rate': 0.2,
        'max_depth': 8,
        'min_child_weight': 0.5,
        'n_estimators': 300,
        'subsample': 1.0
    }
    
    # Dataset configuration
    datasets_info = {
        "topology_A-Duration": {
            "base_path": r"./Dataset/6-Merged_Data/6-Merged_sequence_data_fix_durations/Topology_A_fix_duration_",
            "subsets": ["1s", "2s", "3s", "5s"]
        },
        "topology_B-Duration": {
            "base_path": r"./Dataset/6-Merged_Data/6-Merged_sequence_data_fix_durations/Topology_B_fix_duration_",
            "subsets": ["1s", "2s", "3s", "5s"]
        },
    }
    
    # Output directory
    output_folder = "./Dataset/7-Ablation_CL-XGBoost-dev_type"
    os.makedirs(output_folder, exist_ok=True)
    
    # Storage for comparative results
    results = []
    
    # Iterate through all dataset configurations
    for dataset_name, info in datasets_info.items():
        base_path = info["base_path"]
        subsets = info["subsets"]
        
        for subset in subsets:
            file_path = f"{base_path}{subset}.csv"
            task_name = f"{dataset_name}_{subset}"
            
            # Execute classification task
            result = run_xgboost_classification(
                task_name=task_name,
                file_path=file_path,
                output_folder=output_folder,
                hyperparameters=xgb_hyperparameters
            )
            
            if result is not None:
                results.append({
                    "Dataset": dataset_name,
                    "Window Size": subset,
                    "Accuracy": result["Accuracy"],
                    "Accuracy_std": result["Accuracy_std"],
                    "Precision": result["Precision"],
                    "Precision_std": result["Precision_std"],
                    "Recall": result["Recall"],
                    "Recall_std": result["Recall_std"],
                    "F1-Macro": result["F1-Macro"],
                    "F1-Macro_std": result["F1-Macro_std"],
                    "F1-Weighted": result["F1-Weighted"],
                    "F1-Weighted_std": result["F1-Weighted_std"]
                })
    
    # Generate comparative analysis
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(by=["Dataset", "Window Size"])
    
    print("\n" + "="*80)
    print("COMPREHENSIVE PERFORMANCE COMPARISON")
    print("="*80)
    print(results_df.to_string(index=False))
    print("="*80 + "\n")
    
    # Save comparative results
    results_csv_path = os.path.join(output_folder, "Performance_Comparison_XGBoost.csv")
    results_df.to_csv(results_csv_path, index=False)
    print(f"Comparative results saved: {results_csv_path}\n")
    
    # Visualization: F1-Weighted comparison
    plt.figure(figsize=(14, 8))
    x_pos = np.arange(len(results_df))
    bars = plt.bar(x_pos, results_df["F1-Weighted"], 
                    yerr=results_df["F1-Weighted_std"],
                    capsize=5, alpha=0.8)
    
    # Color bars by dataset
    colors = {'topology_A-Duration': 'steelblue', 'topology_B-Duration': 'darkorange'}
    for bar, dataset in zip(bars, results_df["Dataset"]):
        bar.set_color(colors[dataset])
    
    plt.xlabel("Experimental Configuration", fontsize=14)
    plt.ylabel("F1-Weighted Score", fontsize=14)
    plt.title("XGBoost Performance: F1-Weighted Scores Across Configurations\n(Error bars: ±1 std)", fontsize=16)
    plt.xticks(x_pos, [f"{row['Dataset'].split('-')[0][-1]}-{row['Window Size']}" 
                        for _, row in results_df.iterrows()], 
               rotation=45, ha='right')
    plt.ylim(0, 1.0)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    comparison_plot_path = os.path.join(output_folder, "F1_Weighted_Comparison_XGBoost.png")
    plt.savefig(comparison_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Comparison visualization saved: {comparison_plot_path}")
    
    # Visualization: F1-Macro comparison
    plt.figure(figsize=(14, 8))
    sns.barplot(data=results_df, x="Window Size", y="F1-Macro", hue="Dataset", palette="Set2")
    plt.title("XGBoost Performance: F1-Macro Scores Across Window Sizes", fontsize=16)
    plt.xlabel("Sliding Window Size", fontsize=14)
    plt.ylabel("F1-Macro Score", fontsize=14)
    plt.legend(title="Dataset", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.ylim(0, 1.0)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    f1_macro_plot_path = os.path.join(output_folder, "F1_Macro_Comparison_XGBoost.png")
    plt.savefig(f1_macro_plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"F1-Macro comparison saved: {f1_macro_plot_path}")
    
    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)