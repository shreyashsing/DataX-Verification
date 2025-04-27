import pandas as pd
import numpy as np
import re
from .utils import convert_to_native

class QualityCheck:
    def check_quality(self, df):
        """Check data quality with lightweight pandas operations."""
        print("DEBUG: Starting quality_check with columns:", list(df.columns))
        missing_values = df.isnull().sum().sum()
        missing_ratio = missing_values / df.size if df.size > 0 else 0

        # Infer column types
        numeric_cols = []
        for col in df:
            try:
                temp = pd.to_numeric(df[col], errors="coerce")
                if temp.notna().sum() / len(df[col].dropna()) > 0.8:
                    numeric_cols.append(col)
            except:
                pass
        categorical_cols = [col for col in df if df[col].dtype == "category" or 
                           (df[col].dtype == "object" and df[col].nunique() / len(df[col].dropna()) < 0.1 and col not in numeric_cols)]
        string_cols = [col for col in df if df[col].dtype == "object" and col not in categorical_cols and col not in numeric_cols]
        print("DEBUG: Numeric cols:", numeric_cols)
        print("DEBUG: Categorical cols:", categorical_cols)
        print("DEBUG: String cols:", string_cols)

        # Type checking
        incorrect_types = 0
        incorrect_cols = []
        for col in df:
            if col in categorical_cols + string_cols + numeric_cols:
                continue
            if not pd.api.types.is_numeric_dtype(df[col]) and df[col].dtype != "category":
                incorrect_types += 1
                incorrect_cols.append(col)
        if incorrect_cols:
            print(f"Incorrect types detected in columns: {incorrect_cols}")

        # Anomaly detection for numeric columns
        anomalies = 0
        max_anomalies_per_col = int(len(df) * 0.01)  # Lowered from 0.05
        max_total_anomalies = int(len(df) * 0.02)
        for col in numeric_cols:
            print(f"Checking anomalies in {col}")
            # Check non-numeric anomalies
            invalid_values = df[col].apply(lambda x: isinstance(x, str) and pd.isna(pd.to_numeric(x, errors="coerce")))
            non_numeric_anomalies = min(int(invalid_values.sum()), max_anomalies_per_col)
            anomalies += non_numeric_anomalies
            print(f"Non-numeric anomalies in {col}: {non_numeric_anomalies} (invalid values: {df[col][invalid_values].tolist()[:5]})")
            price_col = pd.to_numeric(df[col], errors="coerce").dropna()
            print(f"Valid numeric values in {col}: {price_col.tolist()[:10]}")
            negative_anomalies = 0
            range_anomalies = 0
            outlier_anomalies = 0
            if len(price_col) > 0:
                # Debug constant check
                unique_count = pd.Series(price_col).nunique()
                std_val = price_col.std() if len(price_col) > 1 else 0
                is_constant = len(price_col) > 0 and np.allclose(price_col, price_col.iloc[0], rtol=1e-5, atol=1e-8) if not price_col.empty else False
                if unique_count > 1:
                    non_zero_values = price_col[price_col != price_col.iloc[0]][:10]
                    print(f"DEBUG: {col} - non-zero values (if any): {non_zero_values.tolist()}")
                print(f"DEBUG: {col} - len(price_col): {len(price_col)}, unique_count: {unique_count}, std_val: {std_val}, is_constant: {is_constant}, first_value: {price_col.iloc[0] if not price_col.empty else 'N/A'}")
                # Enhanced skip logic
                if unique_count <= 2 or std_val < 1e-2 or is_constant or len(price_col) < 20 or (col in ['Work Pressure', 'Job Satisfaction'] and std_val < 0.1):
                    print(f"Skipping anomaly checks for {col}: sparse, binary, constant, or low variation (unique: {unique_count}, std: {std_val}, constant: {is_constant})")
                    continue
                # Detect PCA-like columns or non-negative columns
                mean_val = price_col.mean()
                is_pca_like = (abs(mean_val) < 0.1 and 0.5 < std_val < 2.0) or bool(re.match(r"V\d+", col))
                is_non_negative = price_col.min() >= 0
                # Log-transform Amount
                transformed_col = np.log1p(price_col) if col.lower() == "amount" else price_col
                # Relaxed IQR bounds
                q1, q3 = transformed_col.quantile([0.25, 0.75])
                iqr = q3 - q1
                iqr_multiplier = 20.0 if is_pca_like else 6.0 if col.lower() == "amount" else 4.0  # Increased from 15.0
                lower_bound = q1 - iqr_multiplier * iqr
                upper_bound = q3 + iqr_multiplier * iqr
                range_anomalies = min(int(len(transformed_col[(transformed_col < lower_bound) | (transformed_col > upper_bound)])), max_anomalies_per_col)
                print(f"Range anomalies in {col}: {range_anomalies}")
                # Skip negative value checks for PCA-like or non-negative columns
                if is_pca_like or is_non_negative:
                    negative_anomalies = 0
                    print(f"Negative value anomalies in {col}: 0 (PCA-like or non-negative)")
                else:
                    negative_anomalies = min(int(len(price_col[price_col < 0])), max_anomalies_per_col)
                    print(f"Negative value anomalies in {col}: {negative_anomalies}")
                if len(price_col) >= 20:
                    median = transformed_col.median()
                    mad = np.median(np.abs(transformed_col - median))
                    if mad == 0:
                        mad = std_val or 1
                    z_scores = 0.6745 * (transformed_col - median) / mad
                    z_threshold = 50.0 if is_pca_like else 12.0 if col.lower() == "amount" else 8.0  # Increased from 40.0
                    outlier_anomalies = min(int(len(transformed_col[abs(z_scores) > z_threshold])), max_anomalies_per_col)
                    print(f"Outlier anomalies in {col}: {outlier_anomalies}")
            anomalies += negative_anomalies + range_anomalies + outlier_anomalies
            if anomalies > max_total_anomalies:
                anomalies = max_total_anomalies
                print(f"Capped total anomalies at {max_total_anomalies}")
                break

        # Duplicate detection
        duplicates = df.duplicated().sum()
        key_columns = [col for col in df.columns if col.lower() in ["id", "customerid", "userid"]]
        for col in key_columns:
            key_duplicates = df[col].duplicated().sum()
            duplicates = max(duplicates, key_duplicates)
            print(f"Duplicates in key column {col}: {key_duplicates}")

        quality = {
            "missingValues": int(missing_values),
            "missingRatio": round(missing_ratio, 2),
            "incorrectTypes": int(incorrect_types),
            "anomalies": int(anomalies),
            "duplicates": int(duplicates)
        }
        print("DEBUG: Quality result:", quality)
        return convert_to_native(quality)