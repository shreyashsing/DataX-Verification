# DataX Verification AI

This is the AI verification service for DataX that analyzes and verifies datasets before they're published to the marketplace.

## Setup

1. Create a virtual environment (if not already done):
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt/requirements.txt
   ```

## Running the Verification Server

Start the verification server with:

```
python server.py
```

The server will run on port 5000 by default and provide an API endpoint at `/api/verify` that the web application can call to verify datasets.

## Running the Test Verification Process

To test the verification process with sample datasets:

```
python run_verification.py
```

This will process sample datasets from the `data/input` directory and generate verification reports in `data/output`.

## Integration with DataX Web Application

The web application connects to this verification service to analyze datasets during the publication process. Make sure this server is running when using the "Data Quality" section of the publish workflow.

## API Endpoints

- `POST /api/verify`: Verifies a dataset file
  - Input: FormData with `file` and `name` fields
  - Output: JSON with verification results including quality metrics
