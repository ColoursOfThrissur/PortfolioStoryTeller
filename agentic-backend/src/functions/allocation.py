"""
Allocation Analysis Functions
Calculate asset allocation, sector breakdown, and concentration risk
"""
from typing import Dict, List
import pandas as pd


def calculate_allocation_breakdown(holdings: List[Dict], profiles: Dict) -> Dict:
    """
    Calculate asset allocation and sector breakdown
    
    Args:
        holdings: List of portfolio holdings with ticker, shares
        profiles: Dict of company profiles by ticker
        
    Returns:
        {
            "sectors": {"Technology": 45.2, "Healthcare": 23.1, ...},
            "assets": {"Stocks": 85.0, "Cash": 15.0},
            "top_holdings": [{"ticker": "AAPL", "weight": 12.5}, ...]
        }
    """
    total_value = 0
    sector_values = {}
    holding_values = []
    
    # Calculate individual holding values and sector allocation
    for holding in holdings:
        ticker = holding['ticker']
        shares = holding['shares']
        
        # Get current price (fallback to $100 if not available)
        current_price = 100.0  # This would come from quotes in real implementation
        market_value = shares * current_price
        total_value += market_value
        
        # Get sector from profile
        profile = profiles.get(ticker)
        sector = profile.sector if profile else "Unknown"
        
        if sector not in sector_values:
            sector_values[sector] = 0
        sector_values[sector] += market_value
        
        holding_values.append({
            "ticker": ticker,
            "shares": shares,
            "price": current_price,
            "market_value": market_value,
            "sector": sector
        })
    
    # Calculate percentages
    sector_percentages = {}
    for sector, value in sector_values.items():
        sector_percentages[sector] = (value / total_value * 100) if total_value > 0 else 0
    
    # Top holdings by weight
    holding_values.sort(key=lambda x: x['market_value'], reverse=True)
    top_holdings = []
    for holding in holding_values[:10]:
        weight = (holding['market_value'] / total_value * 100) if total_value > 0 else 0
        top_holdings.append({
            "ticker": holding['ticker'],
            "weight": weight,
            "market_value": holding['market_value'],
            "sector": holding['sector']
        })
    
    return {
        "sectors": sector_percentages,
        "assets": {"Stocks": 100.0},  # Assuming all stocks for now
        "top_holdings": top_holdings,
        "total_value": total_value
    }


def calculate_concentration_risk(holdings: List[Dict]) -> Dict:
    """
    Calculate concentration risk metrics
    
    Returns:
        {
            "top_5_concentration": 65.2,  # % in top 5 holdings
            "top_10_concentration": 85.1,  # % in top 10 holdings
            "herfindahl_index": 0.15,  # Concentration index
            "risk_level": "moderate"
        }
    """
    if not holdings:
        return {"top_5_concentration": 0, "top_10_concentration": 0, "herfindahl_index": 0, "risk_level": "low"}
    
    # Calculate market values (using placeholder prices)
    total_value = 0
    holding_values = []
    
    for holding in holdings:
        market_value = holding['shares'] * 100.0  # Placeholder price
        total_value += market_value
        holding_values.append(market_value)
    
    # Sort by value
    holding_values.sort(reverse=True)
    
    # Calculate concentrations
    top_5_value = sum(holding_values[:5])
    top_10_value = sum(holding_values[:10])
    
    top_5_pct = (top_5_value / total_value * 100) if total_value > 0 else 0
    top_10_pct = (top_10_value / total_value * 100) if total_value > 0 else 0
    
    # Herfindahl Index (sum of squared weights)
    weights = [(value / total_value) for value in holding_values] if total_value > 0 else []
    herfindahl = sum([w**2 for w in weights])
    
    # Risk level assessment
    if top_5_pct > 70:
        risk_level = "high"
    elif top_5_pct > 50:
        risk_level = "moderate"
    else:
        risk_level = "low"
    
    return {
        "top_5_concentration": top_5_pct,
        "top_10_concentration": top_10_pct,
        "herfindahl_index": herfindahl,
        "risk_level": risk_level,
        "number_of_holdings": len(holdings)
    }


def generate_allocation_chart_data(allocation: Dict) -> Dict:
    """
    Generate chart data for allocation visualization
    
    Returns:
        {
            "sector_pie_chart": {...},
            "top_holdings_bar_chart": {...}
        }
    """
    sectors = allocation.get('sectors', {})
    top_holdings = allocation.get('top_holdings', [])
    
    # Sector pie chart data
    sector_chart = {
        "chart_type": "pie",
        "title": "Sector Allocation",
        "data": [
            {"name": sector, "y": percentage}
            for sector, percentage in sectors.items()
        ]
    }
    
    # Top holdings bar chart
    holdings_chart = {
        "chart_type": "bar",
        "title": "Top 10 Holdings",
        "categories": [h['ticker'] for h in top_holdings[:10]],
        "data": [h['weight'] for h in top_holdings[:10]]
    }
    
    return {
        "sector_pie_chart": sector_chart,
        "top_holdings_bar_chart": holdings_chart
    }