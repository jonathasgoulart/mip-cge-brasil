import numpy as np
import os

path = 'output/intermediary/VAB_PI.npy'
if os.path.exists(path):
    data = np.load(path)
    print(f"VAB_PI Shape: {data.shape}")
    print(f"VAB_PI Sum: {np.sum(data)}")
    print(f"VAB_PI Max: {np.max(data)}")
    print("First 10 values:", data[:10])
else:
    print("VAB_PI.npy NOT FOUND")
