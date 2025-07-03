#!/usr/bin/env python3
"""
Script to download spaCy models after pip installation.
This handles the spaCy model download for deployment platforms.
"""

import subprocess
import sys
import spacy

def download_spacy_model():
    """Download the English spaCy model."""
    try:
        # Check if model is already installed
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model 'en_core_web_sm' already installed")
        return True
    except OSError:
        print("📦 Downloading spaCy model 'en_core_web_sm'...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ])
            print("✅ spaCy model downloaded successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download spaCy model: {e}")
            return False

if __name__ == "__main__":
    success = download_spacy_model()
    sys.exit(0 if success else 1) 