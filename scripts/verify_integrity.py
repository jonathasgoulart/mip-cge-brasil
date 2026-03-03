import numpy as np
import os

def mathematical_integrity_check():
    regions = ["Rio_de_Janeiro", "Sao_Paulo", "Centro_Oeste", "Sul", "Norte_Nordeste", "Minas_EspiritoSanto"]
    base_dir = r"c:\Users\jonat\Documents\MIP e CGE\output\final"
    
    print("--- MATHEMATICAL INTEGRITY CHECK ---")
    
    for region in regions:
        a_path = os.path.join(base_dir, f"A_{region}.npy")
        if not os.path.exists(a_path): continue
        
        A = np.load(a_path)
        I = np.eye(A.shape[0])
        
        # 1. Hawkins-Simon Condition (Check if all L elements are non-negative)
        try:
            L = np.linalg.inv(I - A)
            negative_elements = np.sum(L < -1e-10) # Using a small tolerance
            if negative_elements == 0:
                hs_status = "PASSED"
            else:
                hs_status = f"FAILED ({negative_elements} negative elements)"
            
            # 2. Maximum Eigenvalue Check (Perron-Frobenius)
            # The spectral radius of A must be < 1 for the economy to be productive
            eigvals = np.linalg.eigvals(A)
            max_eig = np.abs(eigvals).max()
            pf_status = "PASSED" if max_eig < 1 else f"FAILED (max eigenvalue = {max_eig:.4f})"
            
            print(f"Region: {region}")
            print(f"  Hawkins-Simon: {hs_status}")
            print(f"  Spectral Radius: {max_eig:.4f} ({pf_status})")
            
        except Exception as e:
            print(f"  [ERROR] Regional matrix for {region} could not be validated: {e}")

if __name__ == "__main__":
    mathematical_integrity_check()
