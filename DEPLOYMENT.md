# 🤖 DataX AI Verification Service Deployment

## 📋 Requirements

This service requires:
- Python 3.8+
- spaCy with English language model (`en_core_web_sm`)
- All dependencies in `requirements.txt`

## 🚀 Deployment Options

### Option 1: Render (Recommended)

1. **Connect your GitHub repo** to Render
2. **Use these settings**:
   - **Build Command**: `pip install -r requirements.txt && python install_models.py`
   - **Start Command**: `python server.py`
   - **Environment Variables**: 
     - `NODE_ENV=production`
     - `PORT=5000` (auto-set by Render)

### Option 2: Railway

1. **Connect to Railway** - it will use `railway.toml` automatically
2. **Environment Variables**:
   - `NODE_ENV=production`

### Option 3: Heroku

1. **Use the Procfile** (already configured)
2. **Add buildpack**: `heroku/python`

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python install_models.py

# Start server
python server.py
```

## 🏥 Health Check

- **Endpoint**: `GET /health`
- **Response**: `{"status": "healthy", "service": "DataX AI Verification"}`

## 🌐 API Endpoints

- **POST /api/verify** - Verify dataset files
  - Accepts: CSV, Excel, JSON files
  - Returns: Verification results with quality scores

## 🔍 Troubleshooting

### Common Issues:

1. **spaCy Model Missing**:
   - The service automatically downloads the model on startup
   - If it fails, manually run: `python -m spacy download en_core_web_sm`

2. **Memory Issues**:
   - spaCy models require ~50MB RAM
   - Ensure your deployment platform has sufficient memory

3. **Build Timeouts**:
   - spaCy model download can take 1-2 minutes
   - Increase build timeout if necessary

### Environment Variables:

- `NODE_ENV=production` - Enables production CORS settings
- `PORT` - Server port (auto-set by most platforms)

## 📊 Performance

- **Cold Start**: ~10-15 seconds (includes model loading)
- **Warm Request**: ~1-3 seconds per file
- **Memory Usage**: ~100-200MB
- **File Size Limit**: Up to 10MB recommended 