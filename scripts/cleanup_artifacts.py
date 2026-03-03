
import os
import shutil

def run():
    print("=== CLEANING UP OLD MATRICES AND ARTIFACTS ===")
    
    # 1. Backups to remove
    files_to_remove = [
        'data/processed/2021_final/vab_regional_backup.json',
        'data/processed/2021_final/tax_matrix_backup_telecom.json',
        'output/vab_regional_67s_OLD_2015.json',
        'output/Resultados_MIP_CGE_2021.xlsx' # Remove old locked file if possible
    ]
    
    for f in files_to_remove:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"Deleted: {f}")
            except Exception as e:
                print(f"Could not delete {f}: {e}")
                
    # 2. Promote v2 Excel to Main
    v2 = 'output/Resultados_MIP_CGE_2021_v2.xlsx'
    main = 'output/Resultados_MIP_CGE_2021.xlsx'
    
    if os.path.exists(v2):
        if not os.path.exists(main): # Only if main is gone
            try:
                os.rename(v2, main)
                print(f"Promoted {v2} to {main}")
            except Exception as e:
                print(f"Rename failed: {e}")
        else:
            print(f"Main Excel still exists (Active?). Kept v2 as backup.")
            
    print("Cleanup Complete.")

if __name__ == "__main__":
    run()
