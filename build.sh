#!/bin/bash
# Build script for DataX Verification AI Service

echo "🔧 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Installing spaCy models..."
python -m spacy download en_core_web_sm

echo "✅ Build complete!" 