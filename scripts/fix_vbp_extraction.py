
import pandas as pd
import numpy as np

def run():
    print("=== EXTRACTING CORRECT VBP FROM TABLE 01 FOOTER ===")
    
    path = 'data/processed/mip_2015/01.csv'
    # Read entire file skipping only the first few header lines
    df = pd.read_csv(path, header=None, skiprows=1)
    
    # Total row is identified by "Total" in first column or near there.
    # We found it was line 214 (index 213 approx).
    # Let's find it dynamically.
    total_row = None
    for i in range(len(df)-1, 0, -1):
        if str(df.iloc[i, 0]).strip().lower() == "total":
            total_row = df.iloc[i]
            print(f"Found Total Row at Index {i}")
            break
            
    if total_row is None:
        print("Error: Could not find Total row.")
        return
        
    # Standard Activities are in columns 3 to 69 (0-indexed)
    # Let's check a few values.
    # In my previous check: Total,,11909669, 0, 0, 840186...
    # Col 2: 11909669 (Oferta Total?)
    # Col 3: 0
    # Col 4: 0
    # Col 5: 840186 (Activity 1?)
    
    # We need to align with CI columns.
    # In mrio_engine: ci_nacional.iloc[:67, 3:70]
    # This means CI col 3 is Activity 1.
    
    # Let's check Table 05 (CI) col names to be sure.
    ci_path = 'data/processed/mip_2015/05.csv'
    df_ci = pd.read_csv(ci_path, skiprows=3)
    # Print col headers 3,4,5
    print("CI Column 3 Header:", df_ci.columns[3])
    print("CI Column 4 Header:", df_ci.columns[4])
    
    # If CI col 3 is Activity 1, then Table 01 Total Row col 3 should be Activity 1.
    X_nas = total_row.iloc[3:70].apply(pd.to_numeric, errors='coerce').fillna(0).values
    print(f"Extracted X_nas Shape: {X_nas.shape}")
    print(f"X_nas[50] (Tech): {X_nas[50]:.2f}")
    
    # Save to a temporary file for use
    np.save('output/intermediary/X_nas_corrected.npy', X_nas)
    print("Saved corrected X_nas to output/intermediary/X_nas_corrected.npy")

if __name__ == "__main__":
    run()
