
import numpy as np

def run():
    print("=== INSPECTING X_nacional.npy (EXPORTS) ===")
    try:
        x_nac = np.load('output/intermediary/X_nacional.npy')
        print(f"Shape: {x_nac.shape}")
        print(f"Sum: {np.sum(x_nac):.2f}")
        print(f"Sample: {x_nac[:5]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run()
