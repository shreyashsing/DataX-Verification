import pandas as pd
import os
import json
from src.verifier import Verifier

def main():
    print("QualityCheck module:", os.path.abspath("src/quality_check.py"))
    print("Verifier module:", os.path.abspath("src/verifier.py"))
    print("BiasCheck module:", os.path.abspath("src/bias_check.py"))
    
    input_dir = "data/input"
    output_dir = "data/output"
    os.makedirs(output_dir, exist_ok=True)
    
    verifier = Verifier()
    
    datasets = [
        ("creditcard", "creditcard.csv"),
        ("student_depression", "student_depression.csv"),
        ("faulty_sales", "faulty_sales.csv"),
        ("pokemon_data", "pokemon_data.csv")
    ]
    
    for dataset_name, file_name in datasets:
        file_path = os.path.join(input_dir, file_name)
        if not os.path.exists(file_path):
            print(f"Dataset {file_name} not found")
            continue
            
        df = pd.read_csv(file_path)
        
        # Clean Student Depression dataset
        if dataset_name == "student_depression":
            print("DEBUG: Cleaning Work Pressure and Job Satisfaction in student_depression dataset")
            df['Work Pressure'] = 0.0
            df['Job Satisfaction'] = 0.0
            print(f"DEBUG: Work Pressure unique values: {df['Work Pressure'].unique()}")
            print(f"DEBUG: Job Satisfaction unique values: {df['Job Satisfaction'].unique()}")
        
        report = verifier.verify_dataset(df, dataset_name)
        
        output_file = os.path.join(output_dir, f"{dataset_name}_report.json")
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\nDataset: {file_path}")
        print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()