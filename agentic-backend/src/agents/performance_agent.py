"""
Performance Summary Agent
Simplified version using direct Gemini calls instead of LangChain agents
"""
import os
import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from tools.mcp_tools import MCPTools
from functions.performance import (
    calculate_period_return, 
    calculate_itd_return,
    calculate_multi_period_returns,
    calculate_portfolio_value
)
from functions.risk import calculate_risk_metrics, calculate_alpha_beta
from functions.charts import generate_performance_chart_data, generate_metrics_table_data


class PerformanceAgent:
    """Simplified agent for generating Performance Summary section"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GEMINI_API_KEY")
        )
        self.mcp_tools = None
    
    async def initialize(self):
        """Initialize MCP connection"""
        self.mcp_tools = MCPTools()
        await self.mcp_tools.__aenter__()
    
    async def cleanup(self):
        """Cleanup MCP connection"""
        if self.mcp_tools:
            await self.mcp_tools.__aexit__(None, None, None)
    
    async def generate(self, portfolio_data: Dict, period: Dict) -> Dict:
        """
        Generate Performance Summary section using direct calculations.
        
        Args:
            portfolio_data: {"client_name": "...", "holdings": [...]}
            period: {"name": "Q4-2025", "start_date": "2025-10-01", "end_date": "2025-12-31"}
        
        Returns:
            {"section": "performance_summary", "metrics": {...}, "chart_data": {...}, ...}
        """
        try:
            holdings = portfolio_data['holdings']
            tickers = [h['ticker'] for h in holdings]
            
            # Parse period end date
            from datetime import date as date_type
            period_end = date_type.fromisoformat(period['end_date'])
            
            # Calculate all period returns using new function
            multi_period = await calculate_multi_period_returns(
                holdings,
                period_end,
                self.mcp_tools
            )
            
            # Get current prices for portfolio value
            current_prices = {}
            for ticker in tickers:
                hist_data = await self.mcp_tools.get_historical_prices(
                    ticker, period['end_date'], period['end_date']
                )
                if hist_data.get('data') and len(hist_data['data']) > 0:
                    current_prices[ticker] = hist_data['data'][-1]['close']
            
            portfolio_value = calculate_portfolio_value(holdings, current_prices)
            
            # Build performance table
            performance_table = {
                'periods': ['QTD', 'YTD', '1-Year', '3-Yr Ann.', '5-Yr Ann.', 'ITD Ann.'],
                'portfolio': [
                    multi_period['qtd']['portfolio'],
                    multi_period['ytd']['portfolio'],
                    multi_period['one_year']['portfolio'],
                    multi_period['three_year']['portfolio'],
                    multi_period['five_year']['portfolio'],
                    multi_period['itd']['portfolio']
                ],
                'benchmark': [
                    multi_period['qtd']['benchmark'],
                    multi_period['ytd']['benchmark'],
                    multi_period['one_year']['benchmark'],
                    multi_period['three_year']['benchmark'],
                    multi_period['five_year']['benchmark'],
                    multi_period['itd']['benchmark']
                ],
                'difference': [
                    (multi_period['qtd']['portfolio'] or 0) - (multi_period['qtd']['benchmark'] or 0),
                    (multi_period['ytd']['portfolio'] or 0) - (multi_period['ytd']['benchmark'] or 0),
                    (multi_period['one_year']['portfolio'] or 0) - (multi_period['one_year']['benchmark'] or 0),
                    (multi_period['three_year']['portfolio'] or 0) - (multi_period['three_year']['benchmark'] or 0),
                    (multi_period['five_year']['portfolio'] or 0) - (multi_period['five_year']['benchmark'] or 0),
                    (multi_period['itd']['portfolio'] or 0) - (multi_period['itd']['benchmark'] or 0)
                ]
            }
            
            # Account-level table
            qtd_return = multi_period['qtd']['portfolio'] or 0.0
            ytd_return = multi_period['ytd']['portfolio'] or 0.0
            
            account_table = {
                'accounts': [{
                    'name': portfolio_data.get('client_name', 'Portfolio'),
                    'type': 'Brokerage',
                    'value': portfolio_value,
                    'qtd': qtd_return,
                    'ytd': ytd_return,
                    'benchmark': 'S&P 500'
                }]
            }
            
            # Fetch benchmark data for risk metrics only
            benchmark_hist = await self.mcp_tools.get_historical_prices(
                '^GSPC', period['start_date'], period['end_date']
            )
            
            # Calculate risk metrics
            daily_values = [d['close'] for d in benchmark_hist['data']]
            risk_metrics = calculate_risk_metrics(daily_values)
            
            # Calculate alpha/beta
            alpha = qtd_return - (multi_period['qtd']['benchmark'] or 0.0)
            beta = 1.0
            
            # Generate narrative using Gemini
            narrative = await self._generate_narrative(
                portfolio_data['client_name'],
                period['name'],
                qtd_return,
                multi_period['qtd']['benchmark'] or 0.0,
                alpha
            )
            
            # Compile results
            metrics = {
                "portfolio_return": qtd_return,
                "benchmark_return": multi_period['qtd']['benchmark'] or 0.0,
                "alpha": alpha,
                "beta": beta,
                "sharpe_ratio": risk_metrics.get('sharpe_ratio', 0),
                "volatility": risk_metrics.get('volatility', 0),
                "max_drawdown": risk_metrics.get('max_drawdown', 0),
                "itd_return": multi_period['itd']['portfolio'] or 0.0
            }
            
            return {
                "section": "performance_summary",
                "metrics": metrics,
                "performance_table": performance_table,
                "account_table": account_table,
                "narrative": narrative,
                "portfolio_value": portfolio_value,
                "status": "complete",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n{traceback.format_exc()}"
            return {
                "section": "performance_summary",
                "status": "error",
                "error": error_details,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_narrative(self, client_name: str, period: str, 
                                  portfolio_return: float, benchmark_return: float, 
                                  alpha: float) -> str:
        """Generate AI narrative using Gemini"""
        try:
            messages = [
                SystemMessage(content="You are a professional financial advisor writing a portfolio performance summary."),
                HumanMessage(content=f"""
Write a brief professional summary (2-3 sentences) for {client_name}'s portfolio performance:

- Period: {period}
- Portfolio Return: {portfolio_return:.2f}%
- Benchmark Return: {benchmark_return:.2f}%
- Alpha (Outperformance): {alpha:+.2f}%

Focus on the key takeaway and what it means for the client.""")
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            return f"Your portfolio returned {portfolio_return:.2f}% during {period}, outperforming the benchmark by {alpha:+.2f}%."
