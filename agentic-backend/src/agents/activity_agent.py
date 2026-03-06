"""
Activity Agent - Step 6: Activity summary with transaction parsing
"""
from typing import Dict, List
from pathlib import Path
import pandas as pd
from datetime import datetime


class ActivityAgent:
    """Step 6: Activity Summary with Transaction Support"""
    
    async def execute(self, state_data: Dict) -> Dict:
        """Generate activity summary with transaction parsing"""
        try:
            holdings = state_data.get("holdings", [])
            period = state_data.get("period", {})
            transaction_file = state_data.get("transaction_file")
            
            # Parse transactions if file provided
            if transaction_file and Path(transaction_file).exists():
                transactions = self._parse_transactions(transaction_file, period)
                activity = self._analyze_activity(transactions)
                summary = self._generate_summary(activity, period['name'])
            else:
                # No transaction data
                activity = {
                    'trades': [],
                    'contributions': 0,
                    'withdrawals': 0,
                    'dividends': 0,
                    'fees': 0,
                    'rebalancing': []
                }
                summary = f"No transaction data available for {period['name']}. Portfolio contains {len(holdings)} positions."
            
            return {
                "status": "complete",
                "section": "activity_summary",
                "activity": activity,
                "summary": summary,
                "total_trades": len(activity['trades']),
                "total_dividends": activity['dividends'],
                "total_fees": activity['fees'],
                "net_cashflow": activity['contributions'] - activity['withdrawals']
            }
            
        except Exception as e:
            import traceback
            return {
                "status": "error",
                "error": f"{str(e)}\n{traceback.format_exc()}"
            }
    
    def _parse_transactions(self, file_path: str, period: Dict) -> List[Dict]:
        """Parse transaction file (CSV or Excel)"""
        path = Path(file_path)
        
        # Read file
        if path.suffix == '.csv':
            df = pd.read_csv(path)
        elif path.suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(path)
        else:
            return []
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Parse dates
        date_col = None
        for col in ['date', 'trade date', 'transaction date', 'settle date']:
            if col in df.columns:
                date_col = col
                break
        
        if not date_col:
            return []
        
        df[date_col] = pd.to_datetime(df[date_col])
        
        # Filter by period
        start_date = pd.to_datetime(period['start_date'])
        end_date = pd.to_datetime(period['end_date'])
        df = df[(df[date_col] >= start_date) & (df[date_col] <= end_date)]
        
        # Parse transactions
        transactions = []
        for _, row in df.iterrows():
            trans = {
                'date': row[date_col].strftime('%Y-%m-%d'),
                'type': self._parse_transaction_type(row),
                'ticker': self._get_value(row, ['ticker', 'symbol', 'security']),
                'shares': self._get_value(row, ['shares', 'quantity'], 0),
                'amount': self._get_value(row, ['amount', 'value', 'price'], 0),
                'description': self._get_value(row, ['description', 'memo', 'notes'], '')
            }
            transactions.append(trans)
        
        return transactions
    
    def _parse_transaction_type(self, row) -> str:
        """Determine transaction type"""
        for col in ['type', 'transaction type', 'action']:
            if col in row.index:
                val = str(row[col]).lower()
                if 'buy' in val or 'purchase' in val:
                    return 'BUY'
                elif 'sell' in val or 'sale' in val:
                    return 'SELL'
                elif 'dividend' in val or 'div' in val:
                    return 'DIVIDEND'
                elif 'fee' in val or 'charge' in val:
                    return 'FEE'
                elif 'deposit' in val or 'contribution' in val:
                    return 'DEPOSIT'
                elif 'withdrawal' in val or 'distribution' in val:
                    return 'WITHDRAWAL'
        return 'OTHER'
    
    def _get_value(self, row, columns: List[str], default=None):
        """Get value from row by trying multiple column names"""
        for col in columns:
            if col in row.index and pd.notna(row[col]):
                return row[col]
        return default
    
    def _analyze_activity(self, transactions: List[Dict]) -> Dict:
        """Analyze transactions"""
        trades = []
        contributions = 0
        withdrawals = 0
        dividends = 0
        fees = 0
        
        for trans in transactions:
            if trans['type'] == 'BUY':
                trades.append({
                    'date': trans['date'],
                    'action': 'BUY',
                    'ticker': trans['ticker'],
                    'shares': trans['shares'],
                    'amount': trans['amount']
                })
            elif trans['type'] == 'SELL':
                trades.append({
                    'date': trans['date'],
                    'action': 'SELL',
                    'ticker': trans['ticker'],
                    'shares': trans['shares'],
                    'amount': trans['amount']
                })
            elif trans['type'] == 'DIVIDEND':
                dividends += abs(trans['amount'])
            elif trans['type'] == 'FEE':
                fees += abs(trans['amount'])
            elif trans['type'] == 'DEPOSIT':
                contributions += abs(trans['amount'])
            elif trans['type'] == 'WITHDRAWAL':
                withdrawals += abs(trans['amount'])
        
        return {
            'trades': trades,
            'contributions': contributions,
            'withdrawals': withdrawals,
            'dividends': dividends,
            'fees': fees,
            'rebalancing': []  # Would detect from trade patterns
        }
    
    def _generate_summary(self, activity: Dict, period: str) -> str:
        """Generate activity summary text"""
        parts = []
        
        if activity['trades']:
            parts.append(f"{len(activity['trades'])} trades executed")
        
        if activity['contributions'] > 0:
            parts.append(f"${activity['contributions']:,.0f} contributed")
        
        if activity['withdrawals'] > 0:
            parts.append(f"${activity['withdrawals']:,.0f} withdrawn")
        
        if activity['dividends'] > 0:
            parts.append(f"${activity['dividends']:,.0f} in dividends")
        
        if activity['fees'] > 0:
            parts.append(f"${activity['fees']:,.0f} in fees")
        
        if not parts:
            return f"No activity recorded for {period}"
        
        return f"Activity for {period}: " + ", ".join(parts)
