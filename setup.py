from setuptools import setup, find_packages

setup(
    name="DataX-Verification-AI",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "pandas==2.2.2",
        "numpy==1.26.4",
        "spacy==3.7.4",
        "transformers==4.44.2",
        "ydata-profiling==4.8.3",
        "great-expectations==0.18.12",
        "fairlearn==0.10.0",
        "torch==2.4.1",
        "scikit-learn==1.5.1",
        "python-dotenv==1.0.1",
        "pytest==8.3.2"
    ],
    author="Your Name",
    description="AI model for dataset verification",
    license="MIT"
)