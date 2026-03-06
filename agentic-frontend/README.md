# Agentic Portfolio Story Teller - Frontend

Chat-based UI for conversational portfolio report generation.

## Features

- **Chat Interface**: Conversational interaction with AI agent
- **File Upload**: Parse Excel/CSV portfolio files
- **Real-time Updates**: See agent progress in real-time
- **Interactive Charts**: Highcharts visualizations
- **Performance View**: Display metrics, charts, and narratives

## Setup

### 1. Install Dependencies

```bash
npm install
```

Note: Uses shared node_modules with parent frontend if available.

### 2. Run Development Server

```bash
npm run dev
```

Frontend runs on: http://localhost:5174

## Usage

1. **Start Backend**: Make sure agentic-backend is running on port 8001
2. **Open Browser**: Navigate to http://localhost:5174
3. **Configure**:
   - Enter client name
   - Set period (e.g., Q4-2025)
   - Upload portfolio file
4. **Generate**: Click "Generate Report"
5. **View Results**: See performance summary with charts

## Components

- **ChatInterface**: Main chat component with message history
- **FileUpload**: Portfolio file upload component
- **PerformanceView**: Display performance metrics and charts

## Chat Commands

Type in chat:
- "Client name is John Mitchell" - Set client name
- "Period Q4-2025" - Set report period
- "Generate report" - Start generation

Or use the sidebar form controls.

## Port

Frontend runs on port **5174** (different from original frontend on 5173)

## API Connection

Connects to agentic-backend at http://localhost:8001
