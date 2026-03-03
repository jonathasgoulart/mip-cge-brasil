
import numpy as np

def run():
    print("=== INSPECTING Z_nas AND X_nas (INTER-REGIONAL FLOWS) ===")
    
    paths = {
        "Z_nas": "output/intermediary/Z_nas.npy",
        "X_nas": "output/intermediary/X_nas.npy",
        "Z_nacional": "output/intermediary/Z_nacional.npy",
        "X_nacional": "output/intermediary/X_nacional.npy"
    }
    
    for name, path in paths.items():
        try:
            arr = np.load(path)
            print(f"{name}: Shape {arr.shape}")
        except Exception as e:
            print(f"{name}: Error {e}")

if __name__ == "__main__":
    run()
