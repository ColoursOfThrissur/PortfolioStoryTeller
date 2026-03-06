import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd

df = pd.read_excel('US_Portfolio_Template_Single_Individual.xlsx')
print('Columns:', list(df.columns))
print('\nFirst 3 rows:')
print(df.head(3))
print('\nData types:')
print(df.dtypes)
