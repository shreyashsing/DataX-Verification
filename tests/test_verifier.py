import pytest
from src.verifier import DatasetVerifier

def test_verifier():
    verifier = DatasetVerifier()
    report = verifier.verify_dataset("data/input/sample1.csv", "Finance")
    assert report["qualityScore"] >= 0
    assert isinstance(report["datasetHash"], str)
    assert isinstance(report["verificationHash"], str)