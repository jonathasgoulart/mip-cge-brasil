import numpy as np
import os

def run_labor_policy(new_hours: int = 40, base_hours: int = 44, replacement_rate: float = 1.0):
    # Paths (consistent with estimate_workweek_reduction.py)
    inter_dir = 'output/intermediary'
    final_dir = 'output/final'
    
    A_file = os.path.join(inter_dir, 'A_nas.npy')
    X_file = os.path.join(inter_dir, 'X_nas.npy')
    Emp_file = os.path.join(final_dir, 'emp_coefficients_67x27.npy')
    Inc_file = os.path.join(final_dir, 'inc_coefficients_67x27.npy')
    Label_file = os.path.join(inter_dir, 'sector_labels.txt')

    # Load Data
    A = np.load(A_file)
    X = np.load(X_file)
    emp_coefs_all = np.load(Emp_file)
    inc_coefs_all = np.load(Inc_file)
    
    with open(Label_file, 'r', encoding='latin1') as f:
        labels = [line.strip() for line in f if line.strip()]

    # Use National averages or specific index (0-26)
    # Applying mean across states for a national estimate
    emp_coefs = np.mean(emp_coefs_all, axis=1)
    inc_coefs = np.mean(inc_coefs_all, axis=1)

    ratio = base_hours / new_hours
    
    # 1. Employment Impact (Jobs Created)
    L_base = emp_coefs * X
    L_new = L_base * ratio
    jobs_created = L_new - L_base
    
    # 2. Price Impact (Leontief Price Model)
    # Labor share in Value Added increases by ratio
    v_l_base = inc_coefs / 1_000_000.0 # Reais to Million normalization proxy
    v_l_new = v_l_base * ratio
    delta_v = v_l_new - v_l_base
    
    I = np.eye(A.shape[0])
    L_inv = np.linalg.inv(I - A)
    delta_p = delta_v @ L_inv # Impact in percentage points if normalized correctly
    
    # 3. GDP Impact if replacement_rate < 1.0
    R_req = ratio
    R_act = 1.0 + (R_req - 1.0) * replacement_rate
    E = R_act / R_req
    gdp_impact_pct = (E - 1.0) * 100

    # Sectoral results
    sector_results = []
    for i in range(len(labels)):
        sector_results.append({
            "id": i,
            "name": labels[i],
            "base_jobs": float(L_base[i]),
            "jobs_created": float(jobs_created[i]),
            "price_impact_pct": float(delta_p[i] * 100) # Scaling for readability
        })

    return {
        "summary": {
            "hours_reduction": f"{base_hours}h -> {new_hours}h",
            "ratio": float(ratio),
            "replacement_rate": float(replacement_rate),
            "total_jobs_created": float(np.sum(jobs_created)),
            "avg_price_increase_pct": float(np.mean(delta_p) * 100),
            "gdp_impact_pct": float(gdp_impact_pct)
        },
        "sectors": sector_results
    }
