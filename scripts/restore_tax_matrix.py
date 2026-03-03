
import shutil
import os

def run():
    print("=== RESTORING TAX MATRIX FROM SOURCE ===")
    src = 'output/intermediary/tax_data.json'
    dst = 'data/processed/2021_final/tax_matrix.json'
    
    if os.path.exists(src):
        shutil.copy(src, dst)
        print("Restored tax_matrix.json")
    else:
        print("Source tax_data.json not found! Using existing matrix.")
        
if __name__ == "__main__":
    run()
