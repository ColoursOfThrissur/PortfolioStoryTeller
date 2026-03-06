"""
Holdings Agent - Step 4: Holdings detail table
"""
from typing import Dict, List
from tools.mcp_tools import MCPTools


class HoldingsAgent:
    """Step 4: Holdings Detail"""
    
    async def execute(self, state_data: Dict) -> Dict:
        """Generate holdings detail table with returns"""
        try:
            holdings = state_data.get("holdings", [])
            period = state_data.get("period", {})
            
            async with MCPTools() as mcp:
                holdings_table = []
                total_value = 0
                
                for holding in holdings:
                    ticker = holding['ticker']
                    shares = holding['shares']
                    
                    try:
                        # Get current data
                        quote = await mcp.get_current_quote(ticker)
                        profile = await mcp.get_company_profile(ticker)
                        
                        # Get period prices for return calc
                        hist = await mcp.get_historical_prices(
                            ticker,
                            period['start_date'],
                            period['end_date']
                        )
                        
                        price = quote['price']
                        value = shares * price
                        total_value += value
                        
                        # Calculate return
                        if hist['data'] and len(hist['data']) > 1:
                            start_price = hist['data'][0]['close']
                            end_price = hist['data'][-1]['close']
                            qtd_return = ((end_price - start_price) / start_price * 100) if start_price > 0 else 0
                        else:
                            qtd_return = 0
                        
                        holdings_table.append({
                            'security': ticker,
                            'name': profile.get('name', ticker),
                            'asset_class': profile.get('sector', 'Unknown'),
                            'shares': shares,
                            'price': price,
                            'value': value,
                            'qtd_return': qtd_return
                        })
                    except Exception as e:
                        print(f"Warning: Failed to process {ticker}: {e}")
                        holdings_table.append({
                            'security': ticker,
                            'name': ticker,
                            'asset_class': 'Unknown',
                            'shares': shares,
                            'price': 0,
                            'value': 0,
                            'qtd_return': 0
                        })
                
                # Calculate percentages
                for h in holdings_table:
                    h['percentage'] = (h['value'] / total_value * 100) if total_value > 0 else 0
                
                # Sort by value descending
                holdings_table.sort(key=lambda x: x['value'], reverse=True)
                
                return {
                    "status": "complete",
                    "section": "holdings_detail",
                    "holdings_table": holdings_table,
                    "total_value": total_value,
                    "total_positions": len(holdings_table)
                }
                
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "error": f"{str(e)}\n{traceback.format_exc()}"
            }
