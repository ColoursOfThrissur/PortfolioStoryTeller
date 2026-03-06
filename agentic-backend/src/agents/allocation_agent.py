"""
Allocation Agent - Step 3: Asset allocation breakdown
"""
from typing import Dict, List
from tools.mcp_tools import MCPTools


class AllocationAgent:
    """Step 3: Allocation Overview"""
    
    async def execute(self, state_data: Dict) -> Dict:
        """Generate allocation breakdown with real market data"""
        try:
            holdings = state_data.get("holdings", [])
            tickers = [h['ticker'] for h in holdings]
            
            # Get current prices and profiles via MCP
            async with MCPTools() as mcp:
                quotes = {}
                profiles = {}
                
                for ticker in tickers:
                    try:
                        quote = await mcp.get_current_quote(ticker)
                        profile = await mcp.get_company_profile(ticker)
                        quotes[ticker] = quote['price']
                        profiles[ticker] = profile
                    except Exception as e:
                        print(f"Warning: Failed to fetch data for {ticker}: {e}")
                        quotes[ticker] = 100.0
                        profiles[ticker] = {'sector': 'Unknown', 'name': ticker}
            
            # Calculate allocation
            allocation = self._calculate_allocation(holdings, quotes, profiles)
            
            return {
                "status": "complete",
                "section": "allocation_overview",
                "allocation_table": allocation['table'],
                "sector_breakdown": allocation['sectors'],
                "chart_data": allocation['chart'],
                "total_value": allocation['total_value'],
                "top_holdings": allocation['top_holdings']
            }
            
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "error": f"{str(e)}\n{traceback.format_exc()}"
            }
    
    def _calculate_allocation(self, holdings: List[Dict], prices: Dict, profiles: Dict) -> Dict:
        """Calculate asset allocation with real prices"""
        
        positions = []
        total_value = 0
        
        for holding in holdings:
            ticker = holding['ticker']
            shares = holding['shares']
            price = prices.get(ticker, 0)
            value = shares * price
            total_value += value
            
            profile = profiles.get(ticker, {})
            sector = profile.get('sector', 'Unknown')
            
            positions.append({
                'ticker': ticker,
                'shares': shares,
                'price': price,
                'value': value,
                'sector': sector
            })
        
        positions.sort(key=lambda x: x['value'], reverse=True)
        
        # Group by sector
        sectors = {}
        for pos in positions:
            sector = pos['sector']
            if sector not in sectors:
                sectors[sector] = 0
            sectors[sector] += pos['value']
        
        # Build allocation table
        allocation_table = []
        for sector, value in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
            pct = (value / total_value * 100) if total_value > 0 else 0
            allocation_table.append({
                'asset_class': sector,
                'percentage': pct,
                'value': value
            })
        
        # Top holdings
        top_holdings = []
        for pos in positions[:10]:
            pct = (pos['value'] / total_value * 100) if total_value > 0 else 0
            top_holdings.append({
                'ticker': pos['ticker'],
                'percentage': pct,
                'value': pos['value']
            })
        
        # Chart data
        chart_data = {
            'type': 'pie',
            'labels': [item['asset_class'] for item in allocation_table],
            'values': [item['percentage'] for item in allocation_table]
        }
        
        return {
            'table': allocation_table,
            'sectors': sectors,
            'chart': chart_data,
            'total_value': total_value,
            'top_holdings': top_holdings
        }
