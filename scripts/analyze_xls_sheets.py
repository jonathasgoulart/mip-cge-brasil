
import pandas as pd
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def analyze_xls():
    path = 'data/raw/mip_2015_67.xls'
    xl = pd.ExcelFile(path)
    
    analysis = []
    
    for sheet in xl.sheet_names:
        # Read the first row to get the title (Cell A1)
        # We read the whole first sheet range but just look at top
        temp_df = pd.read_excel(path, sheet_name=sheet, nrows=5, header=None)
        title = str(temp_df.iloc[0, 0]).strip()
        analysis.append({
            "Sheet": sheet,
            "Title": title,
            "Columns_Preview": temp_df.shape[1]
        })
        print(f"Sheet {sheet}: {title[:100]}...")

    # Save summary to a file
    with open('output/intermediary/xls_sheets_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("Official MIP 2015 Sheets Analysis\n")
        f.write("="*40 + "\n")
        for item in analysis:
            f.write(f"Sheet {item['Sheet']}: {item['Title']}\n")

if __name__ == "__main__":
    analyze_xls()
