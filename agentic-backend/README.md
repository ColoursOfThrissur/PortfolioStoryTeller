# Agentic Portfolio Story Teller - Backend

AI-powered conversational portfolio report generation using LangChain and Gemini.

## Features

- **Agentic AI**: LangChain agent with Gemini 2.0 Flash
- **MCP Integration**: Reuses existing MCP server for market data
- **Pure Calculation Functions**: Modular Python functions for calculations
- **WebSocket Support**: Real-time chat interface
- **Performance Summary**: First section implementation

## Setup

### 1. Install Dependencies

```bash
# Use shared venv from parent directory
cd ..
python -m venv venv
venv\Scripts\activate

# Install agentic backend requirements
cd agentic-backend
pip install -r requirements.txt
```

### 2. Configure Environment

Make sure `.env` file in parent directory has:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Run Server

```bash
python api.py
```

Server runs on: http://localhost:8001

## API Endpoints

### HTTP Endpoints

- `GET /api/health` - Health check
- `POST /api/parse-portfolio` - Parse uploaded portfolio file
- `POST /api/generate-performance` - Generate performance summary

### WebSocket

- `WS /ws/chat` - Real-time chat with agent

## Architecture

```
User Request
  ↓
FastAPI Server (api.py)
  ↓
Performance Agent (agents/performance_agent.py)
  ↓
├─ MCP Tools (tools/mcp_tools.py) → MCP Server → Yahoo Finance
├─ Calc Functions (functions/*.py) → Pure Python calculations
└─ Chart Functions (functions/charts.py) → Highcharts JSON
  ↓
Structured Result (JSON)
```

## Calculation Functions

Located in `src/functions/`:

- **performance.py**: Period return, ITD return calculations
- **risk.py**: Volatility, Sharpe ratio, alpha/beta
- **charts.py**: Highcharts JSON generators

## Agent Flow

1. Receives portfolio data + period
2. Plans execution (what data/tools needed)
3. Calls MCP tools to fetch historical prices
4. Calls calculation functions with fetched data
5. Generates chart data
6. Returns structured result

## Testing

```bash
# Test with sample data
curl -X POST http://localhost:8001/api/generate-performance \
  -H "Content-Type: application/json" \
  -d '{
    "portfolio_data": {
      "client_name": "John Mitchell",
      "holdings": [
        {"ticker": "AAPL", "shares": 200, "cost_basis": 30000}
      ]
    },
    "period": {
      "name": "Q4-2025",
      "start_date": "2025-10-01",
      "end_date": "2025-12-31"
    }
  }'
```

## Port

Backend runs on port **8001** (different from original backend on 8000)
