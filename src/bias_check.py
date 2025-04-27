import pandas as pd
import numpy as np
import re
from scipy.stats import skew

class BiasCheck:
    def check_bias(self, df):
        """Check dataset for bias and diversity."""
        print("DEBUG: Starting bias_check with columns:", list(df.columns))
        bias_score = 0
        categorical_cols = [col for col in df if df[col].dtype == "category" or
                           (df[col].dtype == "object" and df[col].nunique() / len(df[col].dropna()) < 0.1)]
        numeric_cols = [col for col in df if pd.api.types.is_numeric_dtype(df[col]) and
                       pd.Series(df[col]).nunique() > 2 and df[col].std() > 1e-3 and len(df[col].dropna()) >= 20]
        print("DEBUG: Categorical cols:", categorical_cols)
        print("DEBUG: Numeric cols:", numeric_cols)

        # Check categorical bias
        cat_bias = 0
        cat_count = 0
        for col in categorical_cols:
            value_counts = df[col].value_counts(normalize=True)
            if len(value_counts) > 1:
                max_proportion = value_counts.max()
                cat_bias += max_proportion
                cat_count += 1
                print(f"Categorical bias in {col}: max proportion = {max_proportion}")
        if cat_count > 0:
            cat_bias /= cat_count
            bias_score += 0.5 * cat_bias
        else:
            cat_bias = 0
        print(f"DEBUG: Categorical bias score: {cat_bias}")

        # Check numeric bias
        num_bias = 0
        num_count = 0
        for col in numeric_cols:
            data = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(data) > 0:
                mean_val = data.mean()
                std_val = data.std()
                is_pca_like = abs(mean_val) < 0.1 and 0.5 < std_val < 2.0
                skewness = abs(skew(data, nan_policy="omit"))
                if not np.isnan(skewness):
                    skew_threshold = 5.0 if is_pca_like else 3.0
                    num_bias += min(skewness / skew_threshold, 1)
                    num_count += 1
                    print(f"Numeric bias in {col}: skewness = {skewness}")
        if num_count > 0:
            num_bias /= num_count
            bias_score += 0.5 * num_bias
        else:
            num_bias = 0
        print(f"DEBUG: Numeric bias score: {num_bias}")

        bias_score = min(max(bias_score, 0), 1)
        bias = "Balanced" if bias_score < 0.5 else "Imbalanced"
        print(f"DEBUG: Final bias: {bias}, bias_score: {bias_score}")

        # Compute diversity
        diversity = 0
        col_count = 0
        for col in df:
            unique_count = df[col].nunique()
            total_count = len(df[col].dropna())
            if total_count > 0:
                is_pca_like = bool(re.match(r"V\d+", col)) or (col in numeric_cols and abs(df[col].mean()) < 0.1 and 0.5 < df[col].std() < 2.0)
                expected_unique = min(total_count, 5 if col in categorical_cols or df[col].nunique() <= 2 else total_count * 2 if is_pca_like else total_count)
                diversity_contribution = min(unique_count / expected_unique, 0.7 if is_pca_like else 1.0)
                diversity += diversity_contribution
                col_count += 1
                print(f"DEBUG: Diversity for {col}: unique_count={unique_count}, expected_unique={expected_unique}, contribution={diversity_contribution}")
        diversity = diversity / col_count if col_count > 0 else 0
        print(f"DEBUG: Final diversity: {diversity}")

        return bias, bias_score, diversity