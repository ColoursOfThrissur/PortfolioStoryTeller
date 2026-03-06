"""
Verify calculation flow for portfolio returns
"""
from datetime import date

# Test data from data_dump.txt
holdings = {
    'AAPL': {'shares': 200, 'cost_basis': 30000, 'current_price': 262.52},
    'MSFT': {'shares': 50, 'cost_basis': 18000, 'current_price': 405.20},
    'GOOGL': {'shares': 150, 'cost_basis': 22500, 'current_price': 303.13},
    'NVDA': {'shares': 50, 'cost_basis': 24000, 'current_price': 183.04},
    'AMZN': {'shares': 25, 'cost_basis': 4500, 'current_price': 216.82}
}

# Period: Q4-2025 (Oct 1 - Dec 31, 2025)
# But Q4-2025 is in the FUTURE! Today is March 2026
# So the system should reject this or cap it to today

print("="*80)
print("CALCULATION VERIFICATION")
print("="*80)

# Current portfolio value
total_current = sum(h['shares'] * h['current_price'] for h in holdings.values())
total_cost = sum(h['cost_basis'] for h in holdings.values())

print(f"\n[CURRENT SNAPSHOT]")
print(f"Total Current Value: ${total_current:,.2f}")
print(f"Total Cost Basis: ${total_cost:,.2f}")
print(f"Inception-to-Date Gain: ${total_current - total_cost:,.2f}")
print(f"Inception-to-Date Return: {(total_current - total_cost) / total_cost * 100:.2f}%")

# For Q4-2025 period return, we need:
# 1. Price on Oct 1, 2025 for each holding
# 2. Price on Dec 31, 2025 (or latest available)
# 3. Calculate: (End Value - Start Value) / Start Value * 100

print(f"\n[PERIOD RETURN CALCULATION]")
print(f"Period: Q4-2025 (Oct 1 - Dec 31, 2025)")
print(f"Issue: Q4-2025 is in the FUTURE (starts Oct 2025, today is March 2026)")
print(f"System should: REJECT or use latest available data")

# Example with dummy period prices
print(f"\n[EXAMPLE WITH REAL PERIOD PRICES]")
print(f"If we had Oct 1, 2025 prices:")

# Simulate period prices (these would come from historical data)
period_start_prices = {
    'AAPL': 250.00,  # Example: AAPL was $250 on Oct 1
    'MSFT': 400.00,
    'GOOGL': 290.00,
    'NVDA': 170.00,
    'AMZN': 210.00
}

period_end_prices = {
    'AAPL': 262.52,  # Current price
    'MSFT': 405.20,
    'GOOGL': 303.13,
    'NVDA': 183.04,
    'AMZN': 216.82
}

start_value = sum(holdings[t]['shares'] * period_start_prices[t] for t in holdings.keys())
end_value = sum(holdings[t]['shares'] * period_end_prices[t] for t in holdings.keys())
period_return = (end_value - start_value) / start_value * 100

print(f"\nPortfolio Value on Oct 1, 2025: ${start_value:,.2f}")
print(f"Portfolio Value on Dec 31, 2025: ${end_value:,.2f}")
print(f"Q4-2025 Return: {period_return:+.2f}%")

print(f"\n[INDIVIDUAL HOLDINGS]")
for ticker, data in holdings.items():
    shares = data['shares']
    start_p = period_start_prices[ticker]
    end_p = period_end_prices[ticker]
    holding_return = (end_p - start_p) / start_p * 100
    print(f"{ticker}: {shares} shares × ${start_p:.2f} → ${end_p:.2f} = {holding_return:+.2f}%")

print(f"\n[BENCHMARK COMPARISON]")
print(f"S&P 500 Q4-2025 Return: (would be calculated from ^GSPC historical data)")
print(f"Example: If S&P returned +3.5% in Q4-2025")
print(f"Alpha = Portfolio Return - Benchmark Return")
print(f"Alpha = {period_return:.2f}% - 3.50% = {period_return - 3.5:+.2f}%")

print(f"\n[KEY POINTS]")
print(f"✓ Period return uses ACTUAL historical prices for the period")
print(f"✓ NOT calculated from cost basis (that's ITD return)")
print(f"✓ Both portfolio and benchmark use same period dates")
print(f"✓ Individual holdings also use period prices")
print(f"✗ Q4-2025 is INVALID (future period)")

print("="*80)
