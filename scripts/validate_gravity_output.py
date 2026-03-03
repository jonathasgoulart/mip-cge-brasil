import numpy as np
import os

OUTPUT_DIR = 'output/final'

def validate():
    path = os.path.join(OUTPUT_DIR, 'A_mrio_official_v4.npy')
    if not os.path.exists(path):
        print("MRIO V4 file not found.")
        return

    A = np.load(path)
    print(f"Matrix loaded. Shape: {A.shape}, Dtype: {A.dtype}")
    
    if np.isnan(A).any():
        print("WARNING: Matrix contains NaNs!")
        n_nans = np.isnan(A).sum()
        print(f"Count: {n_nans}")
    else:
        print("Check Pass: No NaNs.")
        
    if np.isinf(A).any():
        print("WARNING: Matrix contains Infs!")
    else:
        print("Check Pass: No Infs.")
        
    print(f"Max Value: {np.nanmax(A):.4f}")
    print(f"Min Value: {np.nanmin(A):.4f}")

if __name__ == "__main__":
    validate()
