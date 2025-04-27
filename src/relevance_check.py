import spacy
import pandas as pd

class RelevanceCheck:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        self.domains = {
            "Health": ["depression", "stress", "mental", "sleep", "diet", "health"],
            "Finance": ["amount", "transaction", "credit", "balance"],
            "Fraud Detection": ["class", "fraud", "anomaly"],
            "Education": ["cgpa", "academic", "study", "degree"],
            "Sales": ["customer", "price", "sale", "purchase"],
            "Other": []
        }

    def check_relevance(self, df, dataset_name):
        """Determine dataset relevance based on columns and content."""
        score = {domain: 0 for domain in self.domains}
        dataset_name_lower = dataset_name.lower()
        
        # Score based on column names
        for col in df.columns:
            col_lower = col.lower()
            for domain, keywords in self.domains.items():
                for keyword in keywords:
                    if keyword in col_lower:
                        score[domain] += 1
                # Boost for binary target columns
                if col_lower == "class" and pd.Series(df[col]).nunique() == 2:
                    if domain == "Fraud Detection":
                        score[domain] += 3
                    elif domain == "Finance":
                        score[domain] += 1

        # Boost based on dataset name
        if "fraud" in dataset_name_lower or "creditcard" in dataset_name_lower:
            score["Fraud Detection"] += 5
        if "depression" in dataset_name_lower or "health" in dataset_name_lower:
            score["Health"] += 5
        if "sales" in dataset_name_lower or "customer" in dataset_name_lower:
            score["Sales"] += 5

        # Return domain with max score, default to Other
        max_score = max(score.values())
        if max_score == 0:
            return "Other"
        return max(score, key=lambda k: score[k])