# API Endpoints Documentation

## Overview
This document describes the Flask API endpoints implemented for the Vulne_Chatbot frontend connectivity. The Flask server runs on port **7001** (changed from 7000 due to port conflict with AirTunes).

**Base URL**: `http://localhost:7001`

## Implementation Status

### ✅ Fully Functional Endpoints
- `/health` - Health check
- `/chat` - Chat interface (basic functionality)
- `/api/models` - Get available models
- `/login` - User authentication
- `/logout` - User logout
- `/admin` - Admin dashboard
- `/api/guardrails/toggle` - Toggle guardrails
- `/api/guardrails/status` - Get guardrails status

### 🔧 Stub Implementations (MVP)
The following endpoints return mock data for frontend development:

#### Metrics & Monitoring
- `GET /api/metrics` - Returns test metrics
- `GET /api/vulnerabilities/summary` - Returns vulnerability summary  
- `GET /api/metrics/timeseries` - Returns time series data
- `GET /api/test/status` - Returns current test status

#### Testing & Benchmarking
- `GET /api/probes/available` - Returns available security probes
- `POST /api/benchmarks/run` - Starts a benchmark run (mock)
- `GET /api/benchmarks/status/<task_id>` - Gets benchmark status (mock)
- `GET /api/benchmarks/configs` - Gets saved configurations
- `POST /api/benchmarks/configs` - Saves a configuration
- `POST /api/benchmarks/stop` - Stops a benchmark (mock)

#### Reporting
- `GET /api/reports` - Gets list of reports
- `GET /api/reports/export` - Exports a report

#### Session Management
- `GET /session/new` - Creates new session
- `GET /session/history` - Gets session history
- `GET /config` - Gets application configuration

## Endpoint Details

### Health Check
```http
GET /health
```
**Response:**
```json
{
    "status": "healthy",
    "service": "VulnerableApp",
    "version": "0.3.0",
    "environment": "production"
}
```

### Metrics API
```http
GET /api/metrics
```
**Response:**
```json
{
    "total_tests": 100,
    "vulnerabilities_found": 23,
    "success_rate": 0.95,
    "avg_response_time": 1.23,
    "active_guardrails": false,
    "guardrails_mode": "none"
}
```

### Available Probes
```http
GET /api/probes/available
```
**Response:**
```json
[
    {
        "id": "prompt_injection",
        "name": "Prompt Injection",
        "category": "injection",
        "severity": "high",
        "description": "Tests for prompt injection vulnerabilities",
        "enabled": true
    }
]
```

### Run Benchmark
```http
POST /api/benchmarks/run
Content-Type: application/json

{
    "config": {
        "models": ["mistral:latest"],
        "probes": ["prompt_injection"],
        "iterations": 10
    }
}
```
**Response:**
```json
{
    "task_id": "uuid-string",
    "status": "started",
    "estimated_duration": 20,
    "started_at": "2025-09-06T08:00:00"
}
```

### Chat Endpoint
```http
POST /chat
Content-Type: application/json

{
    "message": "User message",
    "model": "mistral:latest"
}
```
**Response:**
```json
{
    "response": "AI response text",
    "intent": "greeting",
    "response_time_ms": 125,
    "conversation_id": "session-id",
    "model_used": "mistral:latest",
    "vulnerability_detected": false,
    "vulnerability_score": 0,
    "leaked_secrets": [],
    "attack_type": "none",
    "guardrails_status": "disabled"
}
```

## CORS Configuration
CORS is enabled for:
- `http://localhost:3000` (React frontend default)
- `http://localhost:7001` (Flask backend)
- `http://localhost:7000` (Legacy support)

## Next Steps for Full Implementation

### 1. **Connect to Real Models** (Priority: HIGH)
- Integrate with Ollama for local models
- Configure OCI GenAI endpoints
- Implement model switching logic

### 2. **Database Integration** (Priority: HIGH)
- Implement proper database schema
- Add persistence for:
  - Test results
  - Benchmark data
  - Session history
  - User preferences

### 3. **Real Guardrails Integration** (Priority: MEDIUM)
- Complete NeMo Guardrails setup
- Add GuardrailsAI support
- Implement guardrail bypass detection

### 4. **Async Task Processing** (Priority: MEDIUM)
- Set up Celery with Redis
- Implement real benchmark execution
- Add progress tracking
- Enable parallel testing

### 5. **WebSocket Support** (Priority: LOW)
- Add Flask-SocketIO
- Implement real-time updates
- Stream test progress
- Live vulnerability detection

### 6. **Enhanced Security Testing** (Priority: MEDIUM)
- Implement actual vulnerability probes
- Add ML-based detection
- Create custom probe generator
- Add defense mechanism testing

### 7. **Production Features** (Priority: LOW)
- Add authentication/authorization
- Implement rate limiting
- Add caching layer
- Set up monitoring/logging

## Testing the API

### Quick Test Script
```bash
# Test all endpoints
BASE_URL="http://localhost:7001"

# Health check
curl -s $BASE_URL/health | python -m json.tool

# Get metrics
curl -s $BASE_URL/api/metrics | python -m json.tool

# Get available probes
curl -s $BASE_URL/api/probes/available | python -m json.tool

# Create session
curl -s $BASE_URL/session/new | python -m json.tool

# Test chat
curl -s -X POST $BASE_URL/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}' | python -m json.tool
```

## Notes
- All stub endpoints return realistic mock data
- Response structures match expected frontend requirements
- Error handling is minimal in stub implementations
- Database queries currently return empty or mock results
- The Flask app must be running on port 7001 for the frontend to connect properly

## Contact
For questions about the API implementation, refer to the main project documentation or the session snapshot from 2025-09-06.
