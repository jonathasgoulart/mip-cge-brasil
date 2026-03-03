import numpy as np
import os

OUTPUT_DIR = 'output/intermediary'

def check():
    path = os.path.join(OUTPUT_DIR, 'vab_matrix_raw.npy')
    if not os.path.exists(path):
        print("File not found.")
        return

    # Load matrix (33, 20)
    mat = np.load(path)
    print(f"Matrix Shape: {mat.shape}")
    
    # Print Sum of VAB (Col 1 to 19) for each row
    # Skip col 0 (Total) if present? slim_extract used sheet_idx 1..19.
    # Col 0 is sheet 0 (usually empty or summary).
    # Step: Print total VAB per Index to identify UFs.
    
    # Known 2021 VAB (approx R$ Billions):
    # SP ~ 2,7 Tn
    # RJ ~ 950 Bn
    # MG ~ 850 Bn
    # RR ~ 18 Bn (Smallest)
    
    print("\n--- VAB Totals per Index (R$ Billions) ---")
    for i in range(mat.shape[0]):
        total = np.sum(mat[i, :]) / 1e9 # Billions
        if total > 0:
            print(f"Index {i}: {total:.2f} B")

if __name__ == "__main__":
    check()
