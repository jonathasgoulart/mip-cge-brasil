
import os
import shutil

def run():
    print("=== CONSOLIDATING FINAL DATA 2021 ===")
    
    src_dir = "output"
    inter_dir = "output/intermediary"
    dest_dir = "data/processed/2021_final"
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        print(f"Created {dest_dir}")
        
    # Valid Files Map
    files_to_move = [
        (os.path.join(src_dir, "vab_regional_67s.json"), os.path.join(dest_dir, "vab_regional.json")),
        (os.path.join(src_dir, "tax_data.json"), os.path.join(dest_dir, "tax_matrix.json")),
        (os.path.join(inter_dir, "VAB_nacional.npy"), os.path.join(dest_dir, "vab_nacional.npy")),
    ]
    
    for src, dst in files_to_move:
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"Promoted: {src} -> {dst}")
        else:
            print(f"ERROR: Source missing {src}")
            
    print("\nSUCCESS: All corrected data is now in 'data/processed/2021_final/'")
    print("Future scripts should reference this folder.")

if __name__ == "__main__":
    run()
