"""
Main Portfolio Report Generator with MCP
"""
import sys
import asyncio
from pathlib import Path
from datetime import date, timedelta
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_ingestion import PortfolioParser
from market_data.mcp_service import MCPMarketDataService
from analytics import AllocationAnalyzer, BenchmarkComparator
from analytics.risk_calculator import RiskCalculator
from analytics.performance_helpers import calculate_period_return, calculate_holding_return, filter_quarters_to_period
from narrative import MarketCommentaryGenerator, PortfolioStoryGenerator, RecommendationEngine
from visualization import ChartGenerator
from reporting.portfolio_story_pdf import PortfolioStoryPDF
from core.models import PerformanceMetrics
from utils import DateUtils, logger
import os


async def generate_portfolio_report(
    portfolio_file: str,
    period_str: str = "Q4-2024",
    output_dir: str = "output/reports"
):
    logger.info("="*60)
    logger.info("Portfolio Report Generator (MCP)")
    logger.info("="*60)
    
    # Step 1: Parse portfolio
    logger.info("\n[1/8] Parsing portfolio...")
    client = PortfolioParser.parse_portfolio_file(portfolio_file)
    validation = PortfolioParser.validate_portfolio(client)
    
    if not validation['valid']:
        logger.error(f"Portfolio validation failed: {validation['issues']}")
        return None
    
    logger.info(f"  Client: {client.name}")
    logger.info(f"  Holdings: {validation['total_holdings']}")
    
    # Step 2-3: Fetch market data and calculate metrics (inside MCP context)
    logger.info("\n[2/8] Fetching market data with MCP...")
    
    # Parse period to get start and end dates
    if 'Q' in period_str:
        year = int(period_str.split('-')[1])
        quarter = int(period_str[1])
        
        if quarter == 1:
            period_start = date(year, 1, 1)
            period_end = date(year, 3, 31)
        elif quarter == 2:
            period_start = date(year, 4, 1)
            period_end = date(year, 6, 30)
        elif quarter == 3:
            period_start = date(year, 7, 1)
            period_end = date(year, 9, 30)
        else:  # Q4
            period_start = date(year, 10, 1)
            period_end = date(year, 12, 31)
    else:
        period_end = date.today()
        period_start = period_end - timedelta(days=90)
    
    # Validate period is not in the future
    today = date.today()
    if period_start > today:
        logger.error(f"\n{'='*60}")
        logger.error(f"ERROR: Period {period_str} is in the future!")
        logger.error(f"Period starts: {period_start}")
        logger.error(f"Today: {today}")
        logger.error(f"Cannot calculate returns for future periods.")
        logger.error(f"{'='*60}\n")
        return None
    
    # Ensure period end is not in the future
    period_end = min(period_end, today)
    
    logger.info(f"  Report Period: {period_start} to {period_end}")
    
    async with MCPMarketDataService() as service:
        # Enrich portfolio with quotes
        tickers = client.get_unique_tickers()
        quotes = await service.get_batch_quotes(tickers)
        
        for account in client.accounts:
            for holding in account.holdings:
                if holding.ticker in quotes:
                    holding.calculate_value(quotes[holding.ticker].current_price)
        
        total_value = client.total_portfolio_value()
        logger.info(f"  Portfolio Value: ${total_value:,.2f}")
        
        # Get company profiles
        logger.info("\n[3/8] Fetching company profiles...")
        profiles = await service.get_batch_profiles(tickers)
        for ticker, profile in profiles.items():
            logger.info(f"  {ticker}: {profile.name} | {profile.sector} | Market Cap: ${profile.market_cap/1e9:.1f}B")
        
        # Get historical data for period calculation
        logger.info("\n[4/8] Calculating performance metrics...")
        benchmark_ticker = "^GSPC"  # S&P 500 Index
        
        # Fetch historical data from period start to today (need extra buffer for data availability)
        hist_start = period_start - timedelta(days=7)  # Small buffer
        hist_end = period_end  # Use period end, not today
        
        # Get period start and end prices for each holding
        logger.info(f"  Fetching historical prices for period {period_start} to {period_end}...")
        period_start_prices = {}
        period_end_prices = {}
        holdings_hist_data = {}
        holdings_period_data = {}  # Store full period data for each holding
        
        for ticker in tickers:
            try:
                hist = await service.get_historical_prices(ticker, hist_start, hist_end)
                holdings_hist_data[ticker] = hist
                
                # Get price at period start
                start_mask = hist.index >= pd.Timestamp(period_start, tz='UTC')
                if start_mask.any():
                    period_start_prices[ticker] = hist[start_mask]['close'].iloc[0]
                    actual_start_date = hist[start_mask].index[0].date()
                else:
                    logger.warning(f"  {ticker}: No data on or after {period_start}")
                    continue
                
                # Get price at period end
                end_mask = hist.index <= pd.Timestamp(period_end, tz='UTC')
                if end_mask.any():
                    period_end_prices[ticker] = hist[end_mask]['close'].iloc[-1]
                    actual_end_date = hist[end_mask].index[-1].date()
                else:
                    # Use latest available price
                    period_end_prices[ticker] = hist['close'].iloc[-1]
                    actual_end_date = hist.index[-1].date()
                
                # Store period data for volatility calculations
                period_mask = (hist.index >= pd.Timestamp(period_start, tz='UTC')) & (hist.index <= pd.Timestamp(period_end, tz='UTC'))
                holdings_period_data[ticker] = hist[period_mask]
                
                logger.info(f"  {ticker}: ${period_start_prices.get(ticker, 0):.2f} ({actual_start_date}) to ${period_end_prices.get(ticker, 0):.2f} ({actual_end_date})")
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.warning(f"  {ticker}: Could not fetch historical data - {e}")
        
        # Calculate portfolio period return
        from analytics.performance_calculator import PerformanceCalculator
        
        logger.info(f"\n  [PERIOD PRICE SUMMARY]")
        logger.info(f"  Period: {period_start} to {period_end}")
        logger.info(f"  Holdings with complete data: {len([t for t in tickers if t in period_start_prices and t in period_end_prices])}/{len(tickers)}")
        
        if len(period_start_prices) == 0 or len(period_end_prices) == 0:
            logger.error(f"\n{'='*60}")
            logger.error(f"CRITICAL: No period price data available!")
            logger.error(f"Cannot calculate period returns without start/end prices.")
            logger.error(f"{'='*60}\n")
            return None
        
        portfolio_period_return = PerformanceCalculator.calculate_period_performance(
            client, period_start_prices, period_end_prices
        )
        
        logger.info(f"  Portfolio {period_str} Return: {portfolio_period_return:.2f}%")
        
        # Get benchmark historical data and calculate period return
        try:
            benchmark_hist = await service.get_historical_prices(benchmark_ticker, hist_start, hist_end)
            
            # Extract period data only
            period_mask = (benchmark_hist.index >= pd.Timestamp(period_start, tz='UTC')) & (benchmark_hist.index <= pd.Timestamp(period_end, tz='UTC'))
            benchmark_period_data = benchmark_hist[period_mask]
            
            # Calculate risk metrics from PERIOD data only
            if len(benchmark_period_data) > 0:
                risk_metrics = RiskCalculator.calculate_all_metrics(benchmark_period_data['close'])
                quarterly_returns = RiskCalculator.calculate_quarterly_returns(benchmark_hist)
            else:
                risk_metrics = {'volatility': None, 'sharpe_ratio': None, 'max_drawdown': None}
                quarterly_returns = pd.DataFrame()
            
            # Calculate actual period return for benchmark
            benchmark_period_return = calculate_period_return(benchmark_hist, period_str, period_end)
            
            if benchmark_period_return is None:
                logger.warning(f"  Benchmark data unavailable for {period_str}")
                benchmark_period_return = 0.0
            
            # Store benchmark historical data for chart
            benchmark_hist_data = benchmark_period_data  # Use period data only
            
            logger.info(f"  Calculated risk metrics from {len(benchmark_period_data)} days (period only)")
            logger.info(f"  Volatility: {risk_metrics.get('volatility', 0):.1f}%")
            logger.info(f"  Sharpe Ratio: {risk_metrics.get('sharpe_ratio', 0):.2f}")
            logger.info(f"  Max Drawdown: {risk_metrics.get('max_drawdown', 0):.1f}%")
            logger.info(f"  Benchmark {period_str} Return: {benchmark_period_return:.2f}%")
        except Exception as e:
            logger.warning(f"Could not fetch benchmark data: {e}")
            risk_metrics = {'volatility': None, 'sharpe_ratio': None, 'max_drawdown': None}
            benchmark_period_return = 0.0
            benchmark_hist_data = None
            benchmark_period_data = None
        
        # Calculate portfolio daily values for risk metrics
        logger.info(f"\n  Calculating portfolio risk metrics...")
        portfolio_daily_values = pd.Series(dtype=float)
        
        if holdings_period_data:
            # Get common dates across all holdings
            all_dates = set()
            for ticker_data in holdings_period_data.values():
                all_dates.update(ticker_data.index)
            all_dates = sorted(all_dates)
            
            # Calculate portfolio value for each date
            daily_values = []
            for dt in all_dates:
                day_value = 0
                for account in client.accounts:
                    for holding in account.holdings:
                        if holding.ticker in holdings_period_data:
                            ticker_data = holdings_period_data[holding.ticker]
                            if dt in ticker_data.index:
                                price = ticker_data.loc[dt, 'close']
                                day_value += holding.shares * price
                if day_value > 0:
                    daily_values.append(day_value)
            
            if len(daily_values) > 1:
                portfolio_daily_values = pd.Series(daily_values)
                portfolio_risk_metrics = RiskCalculator.calculate_all_metrics(portfolio_daily_values)
                logger.info(f"  Portfolio Volatility: {portfolio_risk_metrics.get('volatility', 0):.2f}%")
                logger.info(f"  Portfolio Sharpe: {portfolio_risk_metrics.get('sharpe_ratio', 0):.2f}")
                logger.info(f"  Portfolio Max Drawdown: {portfolio_risk_metrics.get('max_drawdown', 0):.2f}%")
            else:
                portfolio_risk_metrics = risk_metrics  # Fallback to benchmark
        else:
            portfolio_risk_metrics = risk_metrics  # Fallback to benchmark
        
        # Get benchmark quote
        try:
            benchmark_quote = await service.get_quote(benchmark_ticker)
            logger.info(f"  {benchmark_ticker}: ${benchmark_quote.current_price:.2f} ({benchmark_quote.change_percent:+.2f}%)")
        except:
            pass
        
        # Get news from MCP
        logger.info("\n[5/8] Fetching news from MCP...")
        try:
            news = await service.get_news(benchmark_ticker, days=30)
            logger.info(f"  Found {len(news)} news articles for {benchmark_ticker}")
            for article in news[:3]:
                logger.info(f"  - {article.headline[:70]}...")
        except Exception as e:
            news = []
            logger.warning(f"  No news available: {e}")
        
        # Get analyst recommendations and price targets
        logger.info("\n[6/8] Fetching analyst data...")
        analyst_data = {}
        dividends_data = {}
        earnings_data = {}
        institutional_data = {}
        
        for ticker in tickers[:5]:  # Top 5 holdings
            try:
                rec = await service.get_recommendations(ticker)
                target = await service.get_price_target(ticker)
                divs = await service.get_dividends(ticker)
                earnings = await service.get_earnings_dates(ticker)
                institutions = await service.get_institutional_holders(ticker)
                
                if rec:
                    logger.info(f"  {ticker}: Recommendation = {rec.consensus}")
                if target:
                    logger.info(f"  {ticker}: Target = ${target.target_mean:.2f} (Upside: {target.upside_percent:+.1f}%)")
                if not divs.empty:
                    logger.info(f"  {ticker}: {len(divs)} dividends")
                    dividends_data[ticker] = divs
                if earnings:
                    logger.info(f"  {ticker}: Next earnings available")
                    earnings_data[ticker] = earnings
                if institutions:
                    logger.info(f"  {ticker}: {len(institutions)} institutional holders")
                    institutional_data[ticker] = institutions[:5]  # Top 5
                
                analyst_data[ticker] = {'recommendation': rec, 'target': target}
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.warning(f"  {ticker}: No analyst data available")
    
    # Calculate returns - ACTUAL PERIOD RETURNS with portfolio risk metrics
    # Also calculate ITD for context
    total_cost = sum(h.cost_basis or 0 for acc in client.accounts for h in acc.holdings)
    itd_return = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0.0
    
    portfolio_metrics = PerformanceMetrics(
        qtd_return=portfolio_period_return,
        ytd_return=None,
        one_year=None,
        three_year_ann=None,
        five_year_ann=None,
        itd_ann=itd_return,  # Store ITD separately
        sharpe_ratio=portfolio_risk_metrics.get('sharpe_ratio'),
        volatility=portfolio_risk_metrics.get('volatility'),
        max_drawdown=portfolio_risk_metrics.get('max_drawdown')
    )
    
    # Benchmark metrics with actual period return
    benchmark_metrics = PerformanceMetrics(
        qtd_return=benchmark_period_return,
        ytd_return=None,
        one_year=None,
        three_year_ann=None,
        five_year_ann=None
    )
    
    logger.info(f"  Portfolio {period_str} Return: {portfolio_metrics.qtd_return:.2f}%")
    logger.info(f"  Benchmark {period_str} Return: {benchmark_metrics.qtd_return:.2f}%")
    alpha = portfolio_metrics.qtd_return - benchmark_metrics.qtd_return
    logger.info(f"  Alpha (Outperformance): {alpha:+.2f}%")
    
    # Calculate allocations
    allocations = AllocationAnalyzer.calculate_allocation(client)
    concentration = AllocationAnalyzer.calculate_concentration_risk(client)
    
    # Step 4: Generate narratives
    logger.info("\n[5/8] Generating AI narratives...")
    
    story_gen = PortfolioStoryGenerator()
    rec_engine = RecommendationEngine()
    
    executive_summary = story_gen.generate_executive_summary(
        client, portfolio_metrics, benchmark_metrics, period_str
    )
    
    recommendations = rec_engine.generate_recommendations(
        client, allocations, concentration, portfolio_metrics
    )
    
    logger.info(f"  Generated narratives")
    
    # Step 5: Create visualizations
    logger.info("\n[6/8] Creating charts...")
    chart_gen = ChartGenerator()
    
    # Create portfolio vs benchmark chart if we have benchmark data
    chart_path = None
    if benchmark_hist_data is not None and len(benchmark_hist_data) > 0:
        # Create dummy portfolio historical data (normalized from current value)
        portfolio_hist = benchmark_hist_data.copy()
        portfolio_hist['close'] = portfolio_hist['close'] * (total_value / (benchmark_hist_data['close'].iloc[-1] * 100))
        
        chart_path = chart_gen.create_portfolio_vs_benchmark_chart(
            portfolio_hist, benchmark_hist_data, "portfolio_vs_benchmark.png"
        )
        logger.info(f"  Created comparison chart: {chart_path}")
    
    # Step 6: Generate PDF
    logger.info("\n[7/8] Generating PDF report...")
    
    story_pdf = PortfolioStoryPDF(output_dir=output_dir)
    
    SECTOR_MAP = {
        'AAPL': 'Technology', 'MSFT': 'Technology', 'GOOGL': 'Communication Services',
        'AMZN': 'Consumer Cyclical', 'NVDA': 'Technology'
    }
    
    holdings_list = []
    for acc in client.accounts:
        for h in acc.holdings:
            # Get sector from profile
            sector = profiles.get(h.ticker).sector if h.ticker in profiles else 'Technology'
            
            # Calculate ACTUAL period return for this holding
            holding_period_return = 0.0
            if h.ticker in period_start_prices and h.ticker in period_end_prices:
                start_p = period_start_prices[h.ticker]
                end_p = period_end_prices[h.ticker]
                holding_period_return = ((end_p - start_p) / start_p * 100) if start_p > 0 else 0.0
            
            # Get analyst recommendation
            rec_text = ''
            if h.ticker in analyst_data and analyst_data[h.ticker]['recommendation']:
                rec_text = analyst_data[h.ticker]['recommendation'].consensus
            
            holdings_list.append({
                'ticker': h.ticker,
                'name': profiles.get(h.ticker).name if h.ticker in profiles else h.ticker,
                'sector': sector,
                'weight': (h.current_value / total_value * 100) if total_value > 0 else 0,
                'return': holding_period_return,  # ACTUAL period return
                'recommendation': rec_text,
                'target_upside': analyst_data[h.ticker]['target'].upside_percent if h.ticker in analyst_data and analyst_data[h.ticker]['target'] else None
            })
    
    # Filter historical data to relevant quarters
    historical_data = filter_quarters_to_period(quarterly_returns, period_str) if not quarterly_returns.empty else []
    
    # Replace the current period's return in historical data with the actual calculated value
    # to ensure consistency between main metrics and historical table
    if historical_data:
        for i, h in enumerate(historical_data):
            if period_str.replace('-', ' ') in h.get('quarter', ''):
                historical_data[i]['return'] = benchmark_period_return
                logger.info(f"  Updated historical table {h.get('quarter')} to match main metrics: {benchmark_period_return:.2f}%")
    
    # Market intelligence from news
    intelligence = []
    for article in news[:3]:
        intelligence.append({
            'title': article.headline[:50],
            'sentiment': 'Neutral',
            'analysis': article.summary[:100] if article.summary else article.headline[:100]
        })
    
        report_path = story_pdf.generate(
        client=client,
        portfolio_metrics=portfolio_metrics,
        benchmark_metrics=benchmark_metrics,
        period=period_str,
        headline="",  # Will be generated in PDF from metrics
        narrative=executive_summary,
        holdings_data=holdings_list,
        historical_data=historical_data,
        risks=recommendations,
        market_intelligence=intelligence,
        expert_note="Consider diversifying beyond technology to reduce concentration risk.",
        as_of_date=period_end,
        news_articles=news,
        profiles=profiles,
        chart_path=chart_path,
        dividends_data=dividends_data,
        earnings_data=earnings_data,
        institutional_data=institutional_data,
        period_start=period_start,
        period_end=period_end
    )
    
    logger.info(f"  Report saved to: {report_path}")
    
    # Summary
    logger.info("\n[8/8] Report Generation Complete!")
    logger.info("="*60)
    logger.info(f"Client: {client.name}")
    logger.info(f"Period: {period_str} ({period_start} to {period_end})")
    logger.info(f"Portfolio Value: ${total_value:,.2f}")
    logger.info(f"Portfolio Return: {portfolio_metrics.qtd_return:.2f}%")
    logger.info(f"Benchmark Return: {benchmark_metrics.qtd_return:.2f}%")
    logger.info(f"Alpha: {alpha:+.2f}%")
    logger.info(f"Report: {report_path}")
    logger.info("="*60)
    
    return report_path


async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Portfolio Report')
    parser.add_argument('--portfolio', type=str, required=True)
    parser.add_argument('--period', type=str, default='Q4-2024')
    parser.add_argument('--output', type=str, default='output/reports')
    
    args = parser.parse_args()
    
    try:
        report_path = await generate_portfolio_report(
            portfolio_file=args.portfolio,
            period_str=args.period,
            output_dir=args.output
        )
        
        if report_path:
            print(f"\n✓ Report generated: {report_path}")
            return 0
        else:
            print("\n✗ Report generation failed")
            return 1
            
    except Exception as e:
        logger.error(f"Report generation failed: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
