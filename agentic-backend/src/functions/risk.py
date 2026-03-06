"""
Risk Metrics Calculation Functions
"""
from typing import List, Dict
import numpy as np


def calculate_risk_metrics(daily_values: List[float]) -> Dict:
    """
    Calculate volatility, Sharpe ratio, max drawdown from daily portfolio values.
    
    Args:
        daily_values: [100000, 101000, 99500, ...] (portfolio value each day)
    
    Returns:
        {
            "volatility": 18.45,      # Annualized %
            "sharpe_ratio": 0.76,
            "max_drawdown": -13.74,   # %
            "sortino_ratio": 0.89
        }
    """
    if len(daily_values) < 2:
        return {
            "volatility": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "sortino_ratio": 0.0
        }
    
    # Calculate daily returns
    values = np.array(daily_values)
    returns = np.diff(values) / values[:-1]
    
    # Volatility (annualized)
    volatility = np.std(returns) * np.sqrt(252) * 100
    
    # Sharpe Ratio (assuming 4% risk-free rate)
    risk_free_daily = 0.04 / 252
    excess_returns = returns - risk_free_daily
    sharpe_ratio = (np.mean(excess_returns) / np.std(returns)) * np.sqrt(252) if np.std(returns) > 0 else 0
    
    # Max Drawdown
    cumulative = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = np.min(drawdown) * 100
    
    # Sortino Ratio
    downside_returns = returns[returns < 0]
    downside_std = np.std(downside_returns) if len(downside_returns) > 0 else 0
    sortino_ratio = (np.mean(excess_returns) / downside_std) * np.sqrt(252) if downside_std > 0 else 0
    
    return {
        "volatility": float(volatility),
        "sharpe_ratio": float(sharpe_ratio),
        "max_drawdown": float(max_drawdown),
        "sortino_ratio": float(sortino_ratio)
    }


def calculate_alpha_beta(
    portfolio_returns: List[float],
    benchmark_returns: List[float],
    risk_free_rate: float = 0.04
) -> Dict:
    """
    Calculate alpha and beta vs benchmark.
    
    Args:
        portfolio_returns: Daily returns [0.01, -0.005, 0.02, ...]
        benchmark_returns: Daily returns [0.008, -0.003, 0.015, ...]
        risk_free_rate: Annual risk-free rate (default 4%)
    
    Returns:
        {
            "alpha": 7.12,    # Annualized %
            "beta": 1.15
        }
    """
    if len(portfolio_returns) < 2 or len(benchmark_returns) < 2:
        return {"alpha": 0.0, "beta": 1.0}
    
    port_returns = np.array(portfolio_returns)
    bench_returns = np.array(benchmark_returns)
    
    # Calculate beta (covariance / variance)
    covariance = np.cov(port_returns, bench_returns)[0, 1]
    variance = np.var(bench_returns)
    beta = covariance / variance if variance > 0 else 1.0
    
    # Calculate alpha (annualized)
    risk_free_daily = risk_free_rate / 252
    port_excess = np.mean(port_returns) - risk_free_daily
    bench_excess = np.mean(bench_returns) - risk_free_daily
    alpha = (port_excess - beta * bench_excess) * 252 * 100
    
    return {
        "alpha": float(alpha),
        "beta": float(beta)
    }
