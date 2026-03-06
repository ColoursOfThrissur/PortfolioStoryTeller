"""
Chart Data Generation Functions
Returns Highcharts-compatible JSON configurations
"""
from typing import List, Dict
from datetime import datetime


def generate_performance_chart_data(
    portfolio_history: List[Dict],
    benchmark_history: List[Dict]
) -> Dict:
    """
    Generate Highcharts-compatible JSON for performance line chart.
    
    Args:
        portfolio_history: [{"date": "2025-10-01", "value": 100000}, ...]
        benchmark_history: [{"date": "2025-10-01", "value": 5842.63}, ...]
    
    Returns:
        Highcharts configuration dict
    """
    # Normalize to percentage returns from start
    portfolio_start = portfolio_history[0]["value"] if portfolio_history else 1
    benchmark_start = benchmark_history[0]["value"] if benchmark_history else 1
    
    portfolio_data = []
    for item in portfolio_history:
        timestamp = int(datetime.fromisoformat(item["date"]).timestamp() * 1000)
        normalized_return = ((item["value"] - portfolio_start) / portfolio_start) * 100
        portfolio_data.append([timestamp, round(normalized_return, 2)])
    
    benchmark_data = []
    for item in benchmark_history:
        timestamp = int(datetime.fromisoformat(item["date"]).timestamp() * 1000)
        normalized_return = ((item["value"] - benchmark_start) / benchmark_start) * 100
        benchmark_data.append([timestamp, round(normalized_return, 2)])
    
    return {
        "chart": {
            "type": "line",
            "height": 400
        },
        "title": {
            "text": "Portfolio vs Benchmark Performance"
        },
        "xAxis": {
            "type": "datetime",
            "title": {"text": "Date"}
        },
        "yAxis": {
            "title": {"text": "Return (%)"},
            "labels": {"format": "{value}%"}
        },
        "tooltip": {
            "shared": True,
            "valueSuffix": "%",
            "valueDecimals": 2
        },
        "series": [
            {
                "name": "Portfolio",
                "data": portfolio_data,
                "color": "#3498DB"
            },
            {
                "name": "S&P 500",
                "data": benchmark_data,
                "color": "#95A5A6"
            }
        ],
        "credits": {"enabled": False}
    }


def generate_metrics_table_data(metrics: Dict) -> List[Dict]:
    """
    Generate table data for metrics display.
    
    Args:
        metrics: {
            "portfolio_return": 9.88,
            "benchmark_return": 2.76,
            "alpha": 7.12,
            ...
        }
    
    Returns:
        List of row dicts for table rendering
    """
    return [
        {
            "metric": "Portfolio Return",
            "value": f"{metrics.get('portfolio_return', 0):.2f}%",
            "description": "Period return (price-only)"
        },
        {
            "metric": "Benchmark Return",
            "value": f"{metrics.get('benchmark_return', 0):.2f}%",
            "description": "S&P 500 return"
        },
        {
            "metric": "Alpha",
            "value": f"{metrics.get('alpha', 0):+.2f}%",
            "description": "Outperformance vs benchmark"
        },
        {
            "metric": "Beta",
            "value": f"{metrics.get('beta', 1.0):.2f}",
            "description": "Market sensitivity"
        },
        {
            "metric": "Sharpe Ratio",
            "value": f"{metrics.get('sharpe_ratio', 0):.2f}",
            "description": "Risk-adjusted return"
        },
        {
            "metric": "Volatility",
            "value": f"{metrics.get('volatility', 0):.2f}%",
            "description": "Annualized"
        },
        {
            "metric": "Max Drawdown",
            "value": f"{metrics.get('max_drawdown', 0):.2f}%",
            "description": "Largest peak-to-trough decline"
        }
    ]
