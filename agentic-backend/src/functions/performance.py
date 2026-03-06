"""
Performance Calculation Functions
Pure Python functions for return calculations
"""
from typing import List, Dict, Tuple
from datetime import datetime, date, timedelta


def get_quarter_dates(year: int, quarter: int) -> Tuple[date, date]:
    """
    Get start and end dates for a quarter.
    
    Args:
        year: Year (e.g., 2025)
        quarter: Quarter number (1-4)
    
    Returns:
        (start_date, end_date)
    """
    quarter_map = {
        1: (date(year, 1, 1), date(year, 3, 31)),
        2: (date(year, 4, 1), date(year, 6, 30)),
        3: (date(year, 7, 1), date(year, 9, 30)),
        4: (date(year, 10, 1), date(year, 12, 31))
    }
    return quarter_map[quarter]


def annualize_return(total_return_pct: float, years: float) -> float:
    """
    Convert total return to annualized return using CAGR formula.
    
    Args:
        total_return_pct: Total return as percentage (e.g., 50.0 for 50%)
        years: Number of years (e.g., 3.5)
    
    Returns:
        Annualized return as percentage
    """
    if years <= 0:
        return 0.0
    
    if years <= 1:
        return total_return_pct
    
    # CAGR = ((1 + total_return) ^ (1/years)) - 1
    return (((1 + total_return_pct/100) ** (1/years)) - 1) * 100


def calculate_portfolio_value(
    holdings: List[Dict],
    prices: Dict[str, float]
) -> float:
    """
    Calculate total portfolio value at a specific point in time.
    
    Args:
        holdings: [{"ticker": "AAPL", "shares": 200}, ...]
        prices: {"AAPL": 262.52, "MSFT": 405.20, ...}
    
    Returns:
        Total portfolio value in dollars
    """
    total = 0.0
    for holding in holdings:
        ticker = holding["ticker"]
        shares = holding["shares"]
        if ticker in prices:
            total += shares * prices[ticker]
    return total


def infer_inception_date(holdings: List[Dict]) -> date:
    """
    Infer portfolio inception date from cost basis or default to 3 years ago.
    
    Args:
        holdings: List with optional cost_basis field
    
    Returns:
        Estimated inception date
    """
    # For now, default to 3 years ago
    # In production, would parse from cost_basis dates or transactions
    return date.today() - timedelta(days=3*365), Tuple
from datetime import datetime, date, timedelta


def get_quarter_dates(year: int, quarter: int) -> Tuple[date, date]:
    """
    Get start and end dates for a quarter.
    
    Args:
        year: Year (e.g., 2025)
        quarter: Quarter number (1-4)
    
    Returns:
        (start_date, end_date)
    """
    quarter_map = {
        1: (date(year, 1, 1), date(year, 3, 31)),
        2: (date(year, 4, 1), date(year, 6, 30)),
        3: (date(year, 7, 1), date(year, 9, 30)),
        4: (date(year, 10, 1), date(year, 12, 31))
    }
    return quarter_map[quarter]


def annualize_return(total_return_pct: float, years: float) -> float:
    """
    Convert total return to annualized return using CAGR formula.
    
    Args:
        total_return_pct: Total return as percentage (e.g., 50.0 for 50%)
        years: Number of years (e.g., 3.5)
    
    Returns:
        Annualized return as percentage
    """
    if years <= 0:
        return 0.0
    
    if years <= 1:
        return total_return_pct
    
    # CAGR = ((1 + total_return) ^ (1/years)) - 1
    return (((1 + total_return_pct/100) ** (1/years)) - 1) * 100


def calculate_portfolio_value(
    holdings: List[Dict],
    prices: Dict[str, float]
) -> float:
    """
    Calculate total portfolio value at a specific point in time.
    
    Args:
        holdings: [{"ticker": "AAPL", "shares": 200}, ...]
        prices: {"AAPL": 262.52, "MSFT": 405.20, ...}
    
    Returns:
        Total portfolio value in dollars
    """
    total = 0.0
    for holding in holdings:
        ticker = holding["ticker"]
        shares = holding["shares"]
        if ticker in prices:
            total += shares * prices[ticker]
    return total


def infer_inception_date(holdings: List[Dict]) -> date:
    """
    Infer portfolio inception date from cost basis or default to 3 years ago.
    
    Args:
        holdings: List with optional cost_basis field
    
    Returns:
        Estimated inception date
    """
    # For now, default to 3 years ago
    # In production, would parse from cost_basis dates or transactions
    return date.today() - timedelta(days=3*365)


def calculate_period_return(
    holdings: List[Dict],
    start_prices: Dict[str, float],
    end_prices: Dict[str, float]
) -> float:
    """
    Calculate portfolio period return from price changes.
    
    Args:
        holdings: [{"ticker": "AAPL", "shares": 200}, ...]
        start_prices: {"AAPL": 150.00, "MSFT": 350.00, ...}
        end_prices: {"AAPL": 262.52, "MSFT": 405.20, ...}
    
    Returns:
        Period return as percentage (e.g., 9.88)
    """
    start_value = 0
    end_value = 0
    
    for holding in holdings:
        ticker = holding["ticker"]
        shares = holding["shares"]
        
        if ticker in start_prices and ticker in end_prices:
            start_value += shares * start_prices[ticker]
            end_value += shares * end_prices[ticker]
    
    if start_value == 0:
        return 0.0
    
    return ((end_value - start_value) / start_value) * 100


def calculate_itd_return(
    holdings: List[Dict],
    current_prices: Dict[str, float]
) -> float:
    """
    Calculate inception-to-date return from cost basis.
    
    Args:
        holdings: [{"ticker": "AAPL", "shares": 200, "cost_basis": 30000}, ...]
        current_prices: {"AAPL": 262.52, ...}
    
    Returns:
        ITD return as percentage (e.g., 34.15)
    """
    total_cost = 0
    total_value = 0
    
    for holding in holdings:
        ticker = holding["ticker"]
        shares = holding["shares"]
        cost_basis = holding.get("cost_basis", 0)
        
        total_cost += cost_basis
        if ticker in current_prices:
            total_value += shares * current_prices[ticker]
    
    if total_cost == 0:
        return 0.0
    
    return ((total_value - total_cost) / total_cost) * 100


def calculate_holding_return(
    ticker: str,
    shares: float,
    start_price: float,
    end_price: float
) -> float:
    """
    Calculate return for a single holding.
    
    Returns:
        Return as percentage
    """
    if start_price == 0:
        return 0.0
    
    return ((end_price - start_price) / start_price) * 100


async def calculate_multi_period_returns(
    holdings: List[Dict],
    period_end_date: date,
    mcp_tools,
    inception_date: date = None
) -> Dict[str, Dict[str, float]]:
    """
    Calculate returns for all standard periods (QTD, YTD, 1Y, 3Y, 5Y, ITD).
    
    Args:
        holdings: List of holdings with ticker and shares
        period_end_date: Report end date
        mcp_tools: MCP tools instance for fetching prices
        inception_date: Portfolio inception date (optional)
    
    Returns:
        {
            'qtd': {'portfolio': 9.88, 'benchmark': 2.76},
            'ytd': {'portfolio': 18.5, 'benchmark': 15.2},
            ...
        }
    """
    if inception_date is None:
        inception_date = infer_inception_date(holdings)
    
    tickers = [h['ticker'] for h in holdings]
    results = {}
    
    # Define period boundaries
    year = period_end_date.year
    quarter = (period_end_date.month - 1) // 3 + 1
    
    periods = {
        'qtd': get_quarter_dates(year, quarter),
        'ytd': (date(year, 1, 1), period_end_date),
        'one_year': (period_end_date - timedelta(days=365), period_end_date),
        'three_year': (period_end_date - timedelta(days=3*365), period_end_date),
        'five_year': (period_end_date - timedelta(days=5*365), period_end_date),
        'itd': (inception_date, period_end_date)
    }
    
    # Calculate returns for each period
    for period_name, (start_date, end_date) in periods.items():
        try:
            # Fetch portfolio prices
            start_prices = {}
            end_prices = {}
            
            for ticker in tickers:
                hist_data = await mcp_tools.get_historical_prices(
                    ticker, start_date.isoformat(), end_date.isoformat()
                )
                if hist_data.get('data') and len(hist_data['data']) > 0:
                    start_prices[ticker] = hist_data['data'][0]['close']
                    end_prices[ticker] = hist_data['data'][-1]['close']
            
            # Calculate portfolio return
            start_value = calculate_portfolio_value(holdings, start_prices)
            end_value = calculate_portfolio_value(holdings, end_prices)
            
            if start_value > 0:
                total_return = ((end_value - start_value) / start_value) * 100
            else:
                total_return = 0.0
            
            # Annualize if > 1 year
            years = (end_date - start_date).days / 365.25
            portfolio_return = annualize_return(total_return, years)
            
            # Fetch benchmark return
            benchmark_hist = await mcp_tools.get_historical_prices(
                '^GSPC', start_date.isoformat(), end_date.isoformat()
            )
            
            if benchmark_hist.get('data') and len(benchmark_hist['data']) > 0:
                bench_start = benchmark_hist['data'][0]['close']
                bench_end = benchmark_hist['data'][-1]['close']
                bench_total = ((bench_end - bench_start) / bench_start) * 100
                benchmark_return = annualize_return(bench_total, years)
            else:
                benchmark_return = 0.0
            
            results[period_name] = {
                'portfolio': portfolio_return,
                'benchmark': benchmark_return
            }
            
        except Exception as e:
            # If data not available, set to None
            results[period_name] = {
                'portfolio': None,
                'benchmark': None
            }
    
    return results
