import hashlib
import pandas as pd
import numpy as np

def compute_hash(df):
    """Compute SHA-256 hash of the dataset."""
    df_str = df.to_string()
    return "0x" + hashlib.sha256(df_str.encode()).hexdigest()

def convert_to_native(obj):
    """Convert pandas/numpy types to native Python types for JSON serialization."""
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.tolist()
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: convert_to_native(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_native(item) for item in obj]
    return obj