"""
Inspect Excel file to see what's in it
"""
import pandas as pd

file_path = "US_Portfolio_Template_Single_Individual.xlsx"

# Read all sheets
excel_file = pd.ExcelFile(file_path)
print(f"Sheets: {excel_file.sheet_names}\n")

for sheet_name in excel_file.sheet_names:
    print(f"="*80)
    print(f"SHEET: {sheet_name}")
    print(f"="*80)
    
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(f"Columns: {list(df.columns)}")
    print(f"Rows: {len(df)}\n")
    
    print("First 5 rows:")
    print(df.head())
    print("\n")
    
    # Check for ticker/symbol columns
    for col in df.columns:
        if col.lower() in ['ticker', 'symbol', 'stock symbol', 'security']:
            print(f"Found ticker column: {col}")
            print(f"Values: {df[col].dropna().tolist()}")
            print()
    
    # Check for shares columns
    for col in df.columns:
        if col.lower() in ['shares', 'quantity', 'units', 'number of shares']:
            print(f"Found shares column: {col}")
            print(f"Values: {df[col].dropna().tolist()}")
            print()
