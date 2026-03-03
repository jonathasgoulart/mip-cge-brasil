import os
data_dir = 'data/processed/mip_2015'
for i in range(1, 16):
    path = os.path.join(data_dir, f'{i:02d}.csv')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            print(f"{i:02d}: {f.readline().strip()}")
