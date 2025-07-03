git import spacy
import re
import pandas as pd
from .utils import convert_to_native

class PIIDetection:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm", disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"])

    def detect_pii(self, df):
        """Detect PII using spaCy with batch processing."""
        pii_count = 0
        pii_values = set()
        batch_size = 1000

        # Dynamically identify columns to skip (likely IDs, short strings, or categorical)
        skip_cols = [col for col in df if df[col].dtype in ["int64", "float64"] or 
                     df[col].nunique() / len(df[col].dropna()) < 0.1 or
                     col.lower() in ["id", "identifier", "index"]]

        for col in df:
            if col in skip_cols:
                continue
            print(f"Checking PII in {col}")
            for start in range(0, len(df), batch_size):
                batch = df[col][start:start + batch_size].astype(str).str.strip()
                for val in batch:
                    if (val.lower() in ["", "nan"] or 
                        val.isdigit() or 
                        len(val) < 3 or
                        re.match(r"^[A-Za-z0-9-]{1,10}$", val)):
                        continue
                    doc = self.nlp(val)
                    for ent in doc.ents:
                        if ent.label_ == "PERSON" and len(val.split()) <= 2 and val not in pii_values:
                            print(f"Detected entity in {col}: '{val}' as PERSON")
                            pii_values.add(val)
                            pii_count += 1
                    if re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", val) and val not in pii_values:
                        print(f"Detected email in {col}: '{val}'")
                        pii_values.add(val)
                        pii_count += 1
        return pii_count > 0, pii_count