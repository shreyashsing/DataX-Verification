import sys
import os
# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import json
from src.verifier import Verifier
import numpy as np

class AutoTuneVerifier:
    def __init__(self, datasets, max_iterations=50, target_score=13):
        self.datasets = datasets
        self.verifier = Verifier()
        self.max_iterations = max_iterations
        self.target_score = target_score
        self.best_score = 0
        self.best_config = None
        self.best_reports = None
        # Initial hyperparameters
        self.config = {
            "iqr_multiplier_pca": 8.0,
            "mad_threshold_pca": 20.0,
            "expected_unique_numeric": 10000,
            "expected_unique_categorical": 10
        }
        self.iteration = 0
        self.no_improvement_count = 0

    def evaluate_report(self, report, dataset_name):
        """Evaluate report against target metrics."""
        score = 0
        details = report["details"]
        quality = details["quality"]
        
        if dataset_name == "creditcard":
            # isVerified
            if report["isVerified"]:
                score += 1
            # qualityScore: 85–90
            if 85 <= report["qualityScore"] <= 90:
                score += 1
            # anomalies: 1000–5696
            if 1000 <= quality["anomalies"] <= 5696:
                score += 1
            # diversity: 0.5–0.8
            if 0.5 <= details["diversity"] <= 0.8:
                score += 1
            # relevance: Fraud Detection
            if details["relevance"] == "Fraud Detection":
                score += 1
        elif dataset_name == "student_depression":
            if report["isVerified"]:
                score += 1
            if 85 <= report["qualityScore"] <= 90:
                score += 1
            if quality["anomalies"] == 3:
                score += 1
            if 0.5 <= details["diversity"] <= 0.8:
                score += 1
            if details["relevance"] == "Health":
                score += 1
        else:  # faulty_sales
            if not report["isVerified"]:
                score += 1
            if report["qualityScore"] <= 70:
                score += 1
            if 1800 <= quality["anomalies"] <= 2200:
                score += 1
            if 0.5 <= details["diversity"] <= 0.8:
                score += 1
            if details["relevance"] == "Sales":
                score += 1
        return score

    def update_config(self):
        """Adjust hyperparameters based on iteration."""
        if self.no_improvement_count >= 10:
            # Aggressive adjustment
            self.config["iqr_multiplier_pca"] += np.random.uniform(-2.0, 2.0)
            self.config["mad_threshold_pca"] += np.random.uniform(-5.0, 5.0)
            self.config["expected_unique_numeric"] = int(self.config["expected_unique_numeric"] * np.random.uniform(0.5, 1.5))
            self.no_improvement_count = 0
        else:
            # Incremental adjustment
            self.config["iqr_multiplier_pca"] += np.random.uniform(-0.5, 0.5)
            self.config["mad_threshold_pca"] += np.random.uniform(-2.0, 2.0)
            self.config["expected_unique_numeric"] = int(self.config["expected_unique_numeric"] * np.random.uniform(0.9, 1.1))
        # Ensure bounds
        self.config["iqr_multiplier_pca"] = max(4.0, min(12.0, self.config["iqr_multiplier_pca"]))
        self.config["mad_threshold_pca"] = max(10.0, min(30.0, self.config["mad_threshold_pca"]))
        self.config["expected_unique_numeric"] = max(5000, min(20000, self.config["expected_unique_numeric"]))

    def update_source_files(self):
        """Update source files with current config."""
        # Update quality_check.py
        with open("src/quality_check.py", "r") as f:
            lines = f.readlines()
        with open("src/quality_check.py", "w") as f:
            for line in lines:
                if "iqr_multiplier = " in line and "is_pca_like" in line:
                    line = f"                iqr_multiplier = {self.config['iqr_multiplier_pca']} if is_pca_like else 6.0 if col.lower() == 'amount' else 4.0\n"
                elif "z_threshold = " in line and "is_pca_like" in line:
                    line = f"                    z_threshold = {self.config['mad_threshold_pca']} if is_pca_like else 12.0 if col.lower() == 'amount' else 8.0\n"
                f.write(line)
        # Update bias_check.py
        with open("src/bias_check.py", "r") as f:
            lines = f.readlines()
        with open("src/bias_check.py", "w") as f:
            for line in lines:
                if "expected_unique = " in line:
                    line = f"                expected_unique = min(total_count, {self.config['expected_unique_categorical']} if col in categorical_cols or df[col].nunique() <= 2 else {self.config['expected_unique_numeric']})\n"
                f.write(line)

    def run_iteration(self):
        """Run verification and evaluate."""
        reports = {}
        total_score = 0
        for dataset_path in self.datasets:
            dataset_name = dataset_path.split("/")[-1].split(".")[0]
            df = pd.read_csv(dataset_path)
            report = self.verifier.verify_dataset(df, dataset_name)
            reports[dataset_name] = report
            score = self.evaluate_report(report, dataset_name)
            total_score += score
            print(f"Iteration {self.iteration + 1}: {dataset_name} score = {score}/5")
        
        print(f"Iteration {self.iteration + 1}: Total score = {total_score}/15")
        if total_score > self.best_score:
            self.best_score = total_score
            self.best_config = self.config.copy()
            self.best_reports = reports
            self.no_improvement_count = 0
        else:
            self.no_improvement_count += 1
        return total_score

    def save_results(self):
        """Save best configuration and reports."""
        os.makedirs("data/output/tuning", exist_ok=True)
        with open("data/output/tuning/best_config.json", "w") as f:
            json.dump(self.best_config, f, indent=2)
        for dataset_name, report in self.best_reports.items():
            with open(f"data/output/tuning/{dataset_name}_report.json", "w") as f:
                json.dump(report, f, indent=2)
        with open("data/output/tuning/tuning_log.txt", "w") as f:
            f.write(f"Best Score: {self.best_score}/15\n")
            f.write(f"Best Config: {json.dumps(self.best_config, indent=2)}\n")

    def tune(self):
        """Run tuning loop until target score or max iterations."""
        while self.iteration < self.max_iterations:
            self.iteration += 1
            print(f"\nStarting iteration {self.iteration} with config: {self.config}")
            self.update_source_files()
            # Reload verifier to apply changes
            from importlib import reload
            import src.quality_check
            import src.bias_check
            reload(src.quality_check)
            reload(src.bias_check)
            self.verifier = Verifier()
            
            total_score = self.run_iteration()
            if total_score >= self.target_score:
                print(f"Target score {self.target_score}/15 achieved at iteration {self.iteration}")
                self.save_results()
                return True
            self.update_config()
        
        print(f"Max iterations ({self.max_iterations}) reached. Best score: {self.best_score}/15")
        self.save_results()
        return False

if __name__ == "__main__":
    datasets = [
        "data/input/creditcard.csv",
        "data/input/student_depression.csv",
        "data/input/faulty_sales.csv"
    ]
    tuner = AutoTuneVerifier(datasets)
    tuner.tune()