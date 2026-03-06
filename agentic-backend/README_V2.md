# Agentic Portfolio Report System - New Architecture

## 🎯 Overview

Production-ready agentic system for generating client portfolio reports through conversational AI.

### Key Features
- ✅ **Vague Prompt Handling** - Gemini 2.5 Flash interprets unclear user requests
- ✅ **Stateful Conversations** - Remembers context across chat messages
- ✅ **8-Step Workflow** - Systematic report generation with dependencies
- ✅ **Intelligent Planning** - Planner agent orchestrates entire process
- ✅ **Graceful Input Collection** - Asks for missing data conversationally

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER (Vague Prompt)                      │
│          "Generate Q4 report for John Mitchell"             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              PLANNER AGENT (Gemini 2.5 Flash)               │
│  - Interprets user intent                                   │
│  - Determines current step                                  │
│  - Identifies missing inputs                                │
│  - Routes to section agents                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    STATE MANAGER                            │
│  - Tracks completed steps                                   │
│  - Stores collected data                                    │
│  - Maintains section results                                │
│  - Provides context to LLM                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  SECTION AGENTS                             │
│  1. ParametersAgent      - Collect inputs                   │
│  2. PerformanceAgent     - Calculate returns                │
│  3. AllocationAgent      - Asset breakdown                  │
│  4. HoldingsAgent        - Security details                 │
│  5. CommentaryAgent      - Market narrative                 │
│  6. ActivityAgent        - Trades/dividends                 │
│  7. PlanningAgent        - Recommendations                  │
│  8. OutputAgent          - PDF generation                   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
agentic-backend/
├── src/
│   ├── core/
│   │   ├── report_schema.py      # 8-step report definition
│   │   ├── state_manager.py      # Workflow state tracking
│   │   ├── tool_registry.py      # Available tools catalog
│   │   └── orchestrator.py       # Main coordinator
│   ├── agents/
│   │   ├── planner_agent.py      # Brain - interprets & plans
│   │   ├── parameters_agent.py   # Step 1 - collect inputs
│   │   ├── performance_agent.py  # Step 2 - returns
│   │   └── ...                   # Steps 3-8 (to be added)
│   ├── tools/
│   │   ├── mcp_tools.py          # Market data wrappers
│   │   └── calc_tools.py         # Calculation wrappers
│   └── functions/
│       ├── performance.py        # Pure calculation functions
│       ├── risk.py
│       ├── allocation.py
│       └── charts.py
├── api_v2.py                     # FastAPI server
└── test_new_architecture.py      # Test script
```

## 🚀 Quick Start

### 1. Test the Architecture

```bash
cd agentic-backend
python test_new_architecture.py
```

Expected output:
```
✓ Created session: abc-123
User: 'Generate a report for John Mitchell'
Assistant: Please upload the portfolio file to begin.
Type: response
Progress: 0/8

User: 'Q4-2025'
Assistant: Got it! Q4-2025. Now please upload the portfolio file.

User: [uploads file]
Assistant: ✅ Report Parameters complete!
Type: result
Progress: 1/8

🤖 Generating Performance Summary...
✅ Performance Summary complete!
Progress: 2/8
```

### 2. Start API Server

```bash
# Option 1: Use batch file
start_agentic_v2.bat

# Option 2: Manual
cd agentic-backend
python api_v2.py
```

Server runs on: http://localhost:8001

### 3. Test API

```bash
# Create session
curl -X POST http://localhost:8001/api/session/create

# Send message
curl -X POST http://localhost:8001/api/chat/{session_id} \
  -H "Content-Type: application/json" \
  -d '{"content": "Generate Q4 2025 report for John Mitchell"}'
```

## 💬 Example Conversation Flow

```
User: "Generate a report"
Bot:  "I can help! What's the client name and reporting period?"

User: "John Mitchell, Q4 2025"
Bot:  "Got it! Please upload the portfolio file."

User: [uploads file]
Bot:  "✓ Parameters set for John Mitchell - Q4-2025"
      "🤖 Generating Performance Summary..."
      "✅ Performance Summary complete!"
      "Next: Allocation Overview"

User: "Continue"
Bot:  "🤖 Generating Allocation Overview..."
      "✅ Allocation Overview complete!"
      ...
```

## 🧠 How It Works

### 1. Report Schema (System Knowledge)

Defines all 8 steps with dependencies:

```python
REPORT_SCHEMA = {
    "steps": {
        1: {
            "name": "report_parameters",
            "depends_on": [],
            "required_inputs": ["client_name", "period", "portfolio_file"]
        },
        2: {
            "name": "performance_summary",
            "depends_on": [1],
            "required_data": ["holdings", "period", "benchmark"]
        },
        ...
    }
}
```

### 2. Planner Agent (Brain)

Interprets vague prompts using Gemini 2.5 Flash:

```python
User: "Generate report for John"
↓
Planner analyzes:
- Intent: generate_report
- Data provided: client_name="John"
- Missing: period, portfolio_file
↓
Planner asks: "What reporting period? (e.g., Q4-2025)"
```

### 3. State Manager (Memory)

Tracks progress across messages:

```python
{
    "completed_steps": [1, 2],
    "current_step": 3,
    "collected_data": {
        "client_name": "John Mitchell",
        "period": {"name": "Q4-2025", ...},
        "holdings": [...]
    },
    "section_results": {
        "performance_summary": {...},
        "allocation_overview": {...}
    }
}
```

### 4. Section Agents (Executors)

Specialized agents for each step:

```python
# ParametersAgent - Step 1
- Parses portfolio file
- Validates period format
- Sets benchmark

# PerformanceAgent - Step 2
- Fetches historical prices
- Calculates multi-period returns
- Generates charts
```

## 🔧 Configuration

Edit `.env`:

```bash
GEMINI_API_KEY=your_key_here
DEFAULT_BENCHMARK=^GSPC
FIRM_NAME=Your Firm Name
```

## 📊 API Endpoints

### WebSocket (Recommended)

```javascript
const ws = new WebSocket('ws://localhost:8001/ws/chat/{session_id}');

ws.send(JSON.stringify({
    type: 'message',
    content: 'Generate Q4 report',
    file_path: '/path/to/file.xlsx'
}));

ws.onmessage = (event) => {
    const response = JSON.parse(event.data);
    // response.type: 'response' | 'result' | 'error' | 'complete'
    // response.message: User-facing message
    // response.progress: {completed_steps, total_steps, percentage}
};
```

### HTTP (Alternative)

```bash
POST /api/session/create
GET  /api/session/{session_id}
POST /api/upload
POST /api/chat/{session_id}
```

## 🎯 Current Status

### ✅ Implemented (All 8 Steps)
- Report schema (8 steps) ✅
- State manager ✅
- Tool registry ✅
- Planner agent ✅
- Parameters agent (Step 1) ✅
- Performance agent (Step 2) ✅
- Allocation agent (Step 3) ✅
- Holdings agent (Step 4) ✅
- Commentary agent (Step 5) ✅
- Activity agent (Step 6) ✅
- Planning agent (Step 7) ✅
- Output agent (Step 8) ✅
- Orchestrator ✅
- API v2 ✅
- Frontend integration ✅

## 🔍 Testing

```bash
# Test architecture
python test_new_architecture.py

# Test with real file
python test_new_architecture.py --file input/portfolios/sample.xlsx

# Test API
curl http://localhost:8001/api/health
```

## 🆚 vs. Old Architecture

| Feature | Old | New |
|---------|-----|-----|
| **State** | None | Persistent across messages |
| **Planning** | Hardcoded | AI-driven with Gemini |
| **Sections** | 1 (Performance) | 8 (Full report) |
| **Prompts** | Structured only | Vague prompts OK |
| **Dependencies** | None | Automatic checking |
| **Scalability** | Single section | Multi-section workflow |

## 📝 Next Steps

1. **Add remaining agents** (Steps 3-8)
2. **Frontend integration** (Update React UI)
3. **PDF generation** (Step 8 - Output agent)
4. **Redis integration** (Replace in-memory state)
5. **Error recovery** (Resume failed steps)
6. **Multi-user support** (Session management)

## 🐛 Troubleshooting

**Issue**: "Session not found"
- Solution: Create session first with `/api/session/create`

**Issue**: "Agent not implemented"
- Solution: Only Steps 1-2 implemented currently

**Issue**: "Gemini API error"
- Solution: Check `GEMINI_API_KEY` in `.env`

## 📚 Documentation

- [Report Schema](src/core/report_schema.py) - 8-step structure
- [Planner Agent](src/agents/planner_agent.py) - Intent interpretation
- [State Manager](src/core/state_manager.py) - Workflow tracking
- [Orchestrator](src/core/orchestrator.py) - Main coordinator

## 🤝 Contributing

To add a new section agent:

1. Create `src/agents/{section}_agent.py`
2. Implement `execute()` method
3. Register in `orchestrator.py`
4. Update `report_schema.py` if needed

## 📄 License

Proprietary - All rights reserved
