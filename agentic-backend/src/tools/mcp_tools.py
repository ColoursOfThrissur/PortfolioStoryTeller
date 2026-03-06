"""
MCP Tools for LangChain Agent
Simplified wrappers that don't depend on main project models
"""
import asyncio
import json
from typing import Dict, List
from datetime import datetime, date
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPTools:
    """Simplified MCP tool wrappers for agent"""
    
    def __init__(self):
        self.session = None
        self.read_stream = None
        self.write_stream = None
        self.stdio_context = None
    
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def connect(self):
        """Connect to yfmcp server"""
        if self.session is not None:
            return
        
        server_params = StdioServerParameters(
            command="uvx",
            args=["yfmcp@latest"],
            env=None
        )
        
        self.stdio_context = stdio_client(server_params)
        self.read_stream, self.write_stream = await self.stdio_context.__aenter__()
        
        self.session = ClientSession(self.read_stream, self.write_stream)
        await self.session.__aenter__()
        await self.session.initialize()
    
    async def close(self):
        """Close MCP session"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
                self.session = None
            
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
                self.stdio_context = None
        except Exception:
            pass
    
    async def get_historical_prices(
        self,
        ticker: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        Fetch historical daily prices for a ticker.
        
        Args:
            ticker: Stock symbol (e.g., "AAPL")
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
        
        Returns:
            {
                "ticker": "AAPL",
                "data": [
                    {"date": "2025-10-01", "close": 150.00},
                    {"date": "2025-10-02", "close": 151.20},
                    ...
                ]
            }
        """
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date).date()
        end = datetime.fromisoformat(end_date).date()
        
        # Calculate period
        days = (end - start).days
        if days <= 5:
            period = "5d"
        elif days <= 30:
            period = "1mo"
        elif days <= 90:
            period = "3mo"
        elif days <= 180:
            period = "6mo"
        elif days <= 365:
            period = "1y"
        elif days <= 730:
            period = "2y"
        else:
            period = "5y"
        
        result = await self.session.call_tool(
            "yfinance_get_price_history",
            arguments={
                "symbol": ticker,
                "period": period,
                "interval": "1d"
            }
        )
        
        # Parse markdown table
        markdown_table = result.content[0].text
        lines = markdown_table.strip().split('\n')
        data_lines = [line for line in lines[2:] if line.strip() and '|' in line]
        
        data = []
        for line in data_lines:
            cols = [col.strip() for col in line.split('|')[1:-1]]
            if len(cols) >= 5:
                data.append({
                    "date": cols[0],
                    "close": float(cols[4])
                })
        
        return {
            "ticker": ticker,
            "data": data
        }
    
    async def get_current_quote(self, ticker: str) -> Dict:
        """
        Get current price and basic info.
        
        Args:
            ticker: Stock symbol
        
        Returns:
            {
                "ticker": "AAPL",
                "price": 262.52,
                "change": 2.34,
                "change_percent": 0.90
            }
        """
        result = await self.session.call_tool(
            "yfinance_get_ticker_info",
            arguments={"symbol": ticker}
        )
        
        data = json.loads(result.content[0].text)
        
        current_price = data.get('currentPrice') or data.get('regularMarketPrice', 0.0)
        prev_close = data.get('previousClose', current_price)
        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0.0
        
        return {
            "ticker": ticker,
            "price": float(current_price),
            "change": float(change),
            "change_percent": float(change_pct)
        }
    
    async def get_company_profile(self, ticker: str) -> Dict:
        """
        Get company sector, industry, market cap.
        
        Args:
            ticker: Stock symbol
        
        Returns:
            {
                "ticker": "AAPL",
                "name": "Apple Inc.",
                "sector": "Technology",
                "industry": "Consumer Electronics",
                "market_cap": 3858499371008
            }
        """
        result = await self.session.call_tool(
            "yfinance_get_ticker_info",
            arguments={"symbol": ticker}
        )
        
        data = json.loads(result.content[0].text)
        
        return {
            "ticker": ticker,
            "name": data.get('longName') or data.get('shortName', ticker),
            "sector": data.get('sector', 'Unknown'),
            "industry": data.get('industry', 'Unknown'),
            "market_cap": data.get('marketCap', 0)
        }
