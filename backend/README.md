# ECOLOGIA Backend API

FastAPI backend for ESG Carbon Calculator & Report Generator

## Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run server (from backend directory)
python run.py

# Or with uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Important Notes

1. **Run from backend directory**: Always run the server from the `backend/` directory, not from the project root
2. **Environment Variables**: Create `.env` file in the project root (not in backend/):
   ```
   CLIMATIQ_API_KEY=your_key
   GROQ_API_KEY=your_key
   HUGGINGFACE_API_KEY=your_key
   ```
3. **Python Path**: The `run.py` script automatically adds the parent directory to Python path

## API Endpoints

### Emission
- `POST /api/v1/emission/calculate` - Calculate emissions
- `GET /api/v1/emission/sources` - Get available data sources

### Report
- `POST /api/v1/report/generate` - Generate PDF report
- `GET /api/v1/report/download/{filename}` - Download report

### AI
- `POST /api/v1/ai/chat` - Chat with AI assistant

### Health
- `GET /health` - Health check
- `GET /` - API info

## Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test emission calculation
curl -X POST http://localhost:8000/api/v1/emission/calculate \
  -H "Content-Type: application/json" \
  -d '{"category":"Enerji","electricity_kwh":18450,"natural_gas_m3":500,"region":"TR","period":"Monthly"}'
```
