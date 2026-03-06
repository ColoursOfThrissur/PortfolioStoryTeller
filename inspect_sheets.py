import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import pandas as pd

file_path = 'US_Portfolio_Template_Single_Individual.xlsx'
excel_file = pd.ExcelFile(file_path)

print("Sheet names:", excel_file.sheet_names)
print("\n" + "="*80 + "\n")

for sheet_name in excel_file.sheet_names:
    print(f"Sheet: {sheet_name}")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"Columns: {list(df.columns)}")
    print(f"Rows: {len(df)}")
    print(f"First 2 rows:\n{df.head(2)}")
    print("\n" + "="*80 + "\n")
