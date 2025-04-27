import pandas as pd
import hashlib
import json
import os
from .utils import convert_to_native

class DataLoader:
    def load_dataset(self, file_path):
        """Load dataset (CSV, JSON, Parquet)."""
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)
            elif file_path.endswith(".json"):
                df = pd.read_json(file_path)
            elif file_path.endswith(".parquet"):
                df = pd.read_parquet(file_path)
            else:
                raise ValueError("Unsupported file format")
        except Exception as e:
            raise ValueError(f"Failed to load file {file_path}: {str(e)}")

        dataset_str = json.dumps(convert_to_native(df.to_dict(orient="records")))
        dataset_hash = "0x" + hashlib.sha256(dataset_str.encode('utf-8')).hexdigest()
        
        metadata = {
            "rows": len(df),
            "columns": df.columns.tolist(),
            "size_kb": round(os.path.getsize(file_path) / 1024, 2)
        }
        return df, dataset_hash, convert_to_native(metadata)