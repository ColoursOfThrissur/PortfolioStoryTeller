"""
Tool Registry - Defines all available tools for agents
"""

# MCP Tools (via yfinance MCP server)
MCP_TOOLS = {
    "fetch_historical_prices": {
        "description": "Get historical daily prices for a ticker over a date range",
        "inputs": ["ticker", "start_date", "end_date"],
        "output": "DataFrame with OHLCV data",
        "required_for": ["performance_summary", "risk_analysis"]
    },
    "fetch_current_quote": {
        "description": "Get current price and change for a ticker",
        "inputs": ["ticker"],
        "output": "Current price, change, change_percent",
        "required_for": ["allocation_overview", "holdings_detail"]
    },
    "fetch_company_profile": {
        "description": "Get company sector, industry, market cap",
        "inputs": ["ticker"],
        "output": "Company profile with sector/industry",
        "required_for": ["holdings_detail", "allocation_overview"]
    },
    "fetch_market_news": {
        "description": "Get recent news articles for a ticker",
        "inputs": ["ticker", "days"],
        "output": "List of news articles",
        "required_for": ["market_commentary"]
    },
    "fetch_analyst_recommendations": {
        "description": "Get analyst buy/hold/sell consensus",
        "inputs": ["ticker"],
        "output": "Recommendation consensus",
        "required_for": ["market_commentary", "planning_notes"]
    },
    "fetch_price_target": {
        "description": "Get analyst price targets and upside potential",
        "inputs": ["ticker"],
        "output": "Target prices and upside %",
        "required_for": ["planning_notes"]
    },
    "fetch_dividends": {
        "description": "Get dividend history",
        "inputs": ["ticker"],
        "output": "Dividend payment history",
        "required_for": ["activity_summary"]
    }
}

# Calculation Tools (Python functions)
CALC_TOOLS = {
    "calculate_period_return": {
        "description": "Calculate portfolio return for a specific period",
        "inputs": ["holdings", "start_prices", "end_prices"],
        "output": "Period return percentage",
        "module": "functions.performance",
        "required_for": ["performance_summary"]
    },
    "calculate_multi_period_returns": {
        "description": "Calculate returns for QTD, YTD, 1Y, 3Y, 5Y, ITD",
        "inputs": ["holdings", "period_end_date"],
        "output": "Dict with all period returns",
        "module": "functions.performance",
        "required_for": ["performance_summary"]
    },
    "calculate_twr": {
        "description": "Calculate time-weighted return",
        "inputs": ["portfolio_values", "cash_flows"],
        "output": "TWR percentage",
        "module": "functions.performance",
        "required_for": ["performance_summary"]
    },
    "calculate_risk_metrics": {
        "description": "Calculate Sharpe, volatility, max drawdown",
        "inputs": ["daily_returns"],
        "output": "Risk metrics dict",
        "module": "functions.risk",
        "required_for": ["performance_summary", "risk_analysis"]
    },
    "calculate_alpha_beta": {
        "description": "Calculate alpha and beta vs benchmark",
        "inputs": ["portfolio_returns", "benchmark_returns"],
        "output": "Alpha and beta values",
        "module": "functions.risk",
        "required_for": ["performance_summary"]
    },
    "calculate_asset_allocation": {
        "description": "Calculate allocation by asset class/sector",
        "inputs": ["holdings", "current_prices", "profiles"],
        "output": "Allocation breakdown dict",
        "module": "functions.allocation",
        "required_for": ["allocation_overview"]
    },
    "generate_pie_chart": {
        "description": "Generate Highcharts pie chart JSON",
        "inputs": ["allocation_data"],
        "output": "Highcharts config JSON",
        "module": "functions.charts",
        "required_for": ["allocation_overview"]
    },
    "generate_performance_chart": {
        "description": "Generate portfolio vs benchmark line chart",
        "inputs": ["portfolio_history", "benchmark_history"],
        "output": "Highcharts config JSON",
        "module": "functions.charts",
        "required_for": ["performance_summary"]
    },
    "parse_transactions": {
        "description": "Parse and categorize transaction data",
        "inputs": ["transactions", "period"],
        "output": "Categorized transactions",
        "module": "functions.transactions",
        "required_for": ["activity_summary"]
    }
}

# Combined tool registry
ALL_TOOLS = {**MCP_TOOLS, **CALC_TOOLS}


def get_tools_for_section(section_name: str) -> list:
    """Get list of tools required for a section"""
    tools = []
    for tool_name, tool_info in ALL_TOOLS.items():
        if section_name in tool_info.get("required_for", []):
            tools.append(tool_name)
    return tools


def get_tool_description(tool_name: str) -> str:
    """Get human-readable tool description"""
    if tool_name in ALL_TOOLS:
        return ALL_TOOLS[tool_name]["description"]
    return "Unknown tool"
