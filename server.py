from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pandas as pd
import json
import hashlib
import io
import subprocess
import sys

# Download spaCy model if not available
def ensure_spacy_model():
    """Ensure spaCy model is available before starting the server."""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model ready")
        return True
    except OSError:
        print("📦 Downloading spaCy model...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "spacy", "download", "en_core_web_sm"
            ])
            print("✅ spaCy model downloaded")
            return True
        except Exception as e:
            print(f"❌ Failed to download spaCy model: {e}")
            return False

# Ensure model is available before importing modules that use it
if not ensure_spacy_model():
    print("⚠️ Warning: spaCy model not available. Some features may not work.")

from src.verifier import Verifier
from src.utils import compute_hash

app = Flask(__name__)

# Configure CORS for production
if os.environ.get('NODE_ENV') == 'production':
    # In production, only allow your Vercel domain
    allowed_origins = [
        "https://*.vercel.app",
        "https://your-domain.com"  # Replace with your actual domain
    ]
    CORS(app, origins=allowed_origins)
else:
    # In development, allow all origins
    CORS(app)

# Initialize the verifier
verifier = Verifier()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for deployment platforms"""
    return jsonify({'status': 'healthy', 'service': 'DataX AI Verification'}), 200

@app.route('/api/verify', methods=['POST'])
def verify_dataset():
    """
    Endpoint to verify a dataset file.
    Expects a file upload.
    Returns verification results.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Get dataset name from request or use filename
    name = request.form.get('name', os.path.splitext(file.filename)[0])
    
    try:
        # Read the file based on extension
        file_content = file.read()
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension == '.csv':
            df = pd.read_csv(io.BytesIO(file_content))
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(io.BytesIO(file_content))
        elif file_extension == '.json':
            df = pd.read_json(io.BytesIO(file_content))
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
        
        # Verify the dataset
        verification_result = verifier.verify_dataset(df, name)
        
        # Generate IPFS CID (mock for now)
        dataset_hash = verification_result['datasetHash']
        mock_cid = f"ipfs://{hashlib.sha256(file_content).hexdigest()[:16]}"
        verification_result['details']['datasetCID'] = mock_cid
        
        return jsonify({
            'isVerified': verification_result['isVerified'],
            'verificationHash': verification_result['verificationHash'],
            'datasetHash': dataset_hash,
            'qualityScore': verification_result['qualityScore'],
            'details': {
                'missingValues': verification_result['details']['quality']['missingRatio'] * 100,
                'anomaliesDetected': verification_result['details']['quality']['anomalies'],
                'biasScore': verification_result['details']['bias_score'],
                'piiDetected': verification_result['details']['pii_detected'],
                'overallQuality': verification_result['qualityScore'],
                'diversity': verification_result['details']['diversity'],
                'duplicates': verification_result['details']['quality']['duplicates'],
                'datasetCID': mock_cid,
                'analysisReport': verification_result['analysisReport']
            }
        })
    
    except Exception as e:
        print(f"Error processing file: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 