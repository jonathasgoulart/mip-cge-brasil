import numpy as np
import pandas as pd
import os

# --- Configuration ---
# Paths
BASE_PATH = "output"
INTERMEDIARY_PATH = os.path.join(BASE_PATH, "intermediary")
FINAL_PATH = os.path.join(BASE_PATH, "final")
OUTPUT_REPORT = os.path.join(BASE_PATH, "work_week_reduction_impact.md")

# Files
A_MATRIX_FILE = os.path.join(INTERMEDIARY_PATH, "A_nas.npy")
X_VECTOR_FILE = os.path.join(INTERMEDIARY_PATH, "X_nas.npy")
EMP_COEFFS_FILE = os.path.join(os.path.dirname(INTERMEDIARY_PATH), "final", "emp_coefficients_67x27.npy")
INC_COEFFS_FILE = os.path.join(os.path.dirname(INTERMEDIARY_PATH), "final", "inc_coefficients_67x27.npy")
SECTOR_LABELS_FILE = os.path.join(INTERMEDIARY_PATH, "sector_labels.txt")

# Scenarios
SCENARIOS = {
    "40h": {"old": 44, "new": 40},
    "36h": {"old": 44, "new": 36}
}
REPLACEMENT_RATES = [0.20, 0.40, 0.60, 0.80, 1.00]

def load_data():
    print("Loading data...")
    A = np.load(A_MATRIX_FILE)
    X = np.load(X_VECTOR_FILE)
    emp_coefs = np.load(EMP_COEFFS_FILE)
    inc_coefs = np.load(INC_COEFFS_FILE)
    
    with open(SECTOR_LABELS_FILE, "r", encoding="utf-8") as f:
        sectors = [line.strip() for line in f.readlines() if line.strip()]
        
    # Validation
    assert A.shape == (67, 67), f"Matrix A shape mismatch: {A.shape}"
    assert len(sectors) == 67, f"Sector labels count mismatch: {len(sectors)}"
    
    return A, X, emp_coefs, inc_coefs, sectors

def calculate_employment_impact(X, emp_coefs, ratio):
    """
    Calculates the potential new jobs if work week is reduced.
    Assumption: To maintain Output (X), total labor hours must stay constant.
    If hours/worker (h) drops to h', workers (L) must rise to L'.
    L * h = L' * h' => L' = L * (h / h')
    """
    L_base = emp_coefs * X
    L_new = L_base * ratio
    jobs_created = L_new - L_base
    return jobs_created, L_base

def calculate_price_impact(A, inc_coefs, ratio):
    """
    Calculates the price increase due to labor cost shock.
    Assumption: Monthly wage is fixed, so hourly wage rises.
    Cost of labor per unit of output (v_l) increases by the ratio.
    """
    # Normalize Labor Share (Reais -> Share)
    # inc_coefs are in "Reais per Million Output", so divide by 1e6
    v_l_base = inc_coefs / 1_000_000.0
    
    # New labor cost share
    v_l_new = v_l_base * ratio
    
    # Change in Value Added ("Shock")
    delta_v = v_l_new - v_l_base
    
    # Leontief Price Model: delta_p = delta_v * (I - A)^-1
    I = np.eye(A.shape[0])
    L_inv = np.linalg.inv(I - A)
    
    delta_p = delta_v @ L_inv
    return delta_p * 100  # Convert to percentage

def calculate_gdp_impact(ratio, replacement_rate):
    """
    Calculates the GDP Loss if we cannot replace all workers.
    Assumption: Linear Leontief constraint.
    Output Ratio = Effective Labor Ratio
    """
    # Required Labor Ratio (e.g. 1.10)
    R_req = ratio
    
    # Actual Labor Ratio we manage to get
    # If rep_rate = 0.2, we add 20% of the needed extra workers.
    # R_act = 1 + (0.10 * 0.2) = 1.02
    R_act = 1.0 + (R_req - 1.0) * replacement_rate
    
    # Effective Capacity (Constraint)
    # E = 1.02 / 1.10 = 0.927
    E = R_act / R_req
    
    # GDP Impact (%)
    # Loss = (0.927 - 1) = -0.073 (-7.3%)
    gdp_impact_pct = (E - 1.0) * 100
    
    return gdp_impact_pct

def generate_report(results, sectors):
    print(f"Generating report at {OUTPUT_REPORT}...")
    
    # Create DataFrame for analysis
    df = pd.DataFrame({"Sector": sectors})
    
    # Add calculations for Base Scenario
    df["Base_Jobs"] = results["base_jobs"]
    
    # Add scenarios
    summary_md = "# Impacto da Redução da Jornada de Trabalho (Estimativa MIP)\n\n"
    summary_md += "> **Nota:** Esta estimativa assume produtividade constante (limite superior para empregos) e rigidez salarial (limite superior para preços).\n\n"
    
    summary_md += "## 📊 Resumo Executivo (Cenário Teto: 100% Reposição)\n\n"
    summary_md += "| Cenário | Redução | Fator de Ajuste | Novos Empregos (Total) | Aumento Médio de Preços |\n"
    summary_md += "|---|---|---|---|---|\n"

    for name, data in results["scenarios"].items():
        total_jobs = np.sum(data["jobs_created"])
        avg_price = np.mean(data["price_delta"])
        
        summary_md += f"| {name} | {data['desc']} | {data['ratio']:.2f}x | **+{total_jobs:,.0f}** | **+{avg_price:.2f}%** |\n"
        
        df[f"Jobs_{name}"] = data["jobs_created"]
        df[f"Price_{name}_%"] = data["price_delta"]

    summary_md += "\n---\n\n"

    # --- NEW SECTION: LABOR SHORTAGE ---
    summary_md += "## 📉 Impacto no PIB em Cenário de Escassez de Mão de Obra\n\n"
    summary_md += "Estimativa de perda do PIB caso as empresas **não consigam contratar** todos os trabalhadores necessários para manter a produção.\n\n"
    
    summary_md += "| Taxa de Reposição | Cenário | PIB Impacto (%) | PIB Efetivo (%) |\n"
    summary_md += "|---|---|---|---|\n"
    
    for name, data in results["scenarios"].items():
        for rep_rate in REPLACEMENT_RATES:
            gdp_loss = calculate_gdp_impact(data['ratio'], rep_rate)
            rep_pct = rep_rate * 100
            summary_md += f"| {rep_pct:.0f}% | {name} ({data['desc']}) | **{gdp_loss:.2f}%** | {100+gdp_loss:.2f}% |\n"
    
    summary_md += "\n> **Interpretação**: Se reduzirmos para 40h e conseguirmos repor apenas 20% das vagas necessárias, o PIB cairá **7.3%** por falta de braços.\n\n"
    summary_md += "\n---\n\n"

    # Top 10 Job Creators (40h)
    top_jobs = df.sort_values(by="Jobs_40h", ascending=False).head(10)
    summary_md += "## 🏆 Top 10 Setores: Geração de Empregos (Cenário 40h - Teórico)\n\n"
    summary_md += "| Setor | Ocupações Atuais | + Novas Vagas (40h) | Aumento %\n"
    summary_md += "|---|---|---|---|\n"
    for _, row in top_jobs.iterrows():
        pct = (row['Jobs_40h'] / row['Base_Jobs']) * 100
        summary_md += f"| {row['Sector']} | {row['Base_Jobs']:,.0f} | **+{row['Jobs_40h']:,.0f}** | +{pct:.1f}%\n"

    summary_md += "\n---\n\n"

    # Top 10 Price Impacts (40h)
    top_prices = df.sort_values(by="Price_40h_%", ascending=False).head(10)
    summary_md += "## 💸 Top 10 Setores: Impacto nos Preços (Cenário 40h)\n\n"
    summary_md += "| Setor | Impacto no Preço (%) |\n"
    summary_md += "|---|---|\n"
    for _, row in top_prices.iterrows():
        summary_md += f"| {row['Sector']} | **+{row['Price_40h_%']:.2f}%** |\n"

    summary_md += "\n---\n\n"
    summary_md += "## 📋 Tabela Completa (Por Setor)\n\n"
    summary_md += df.to_markdown(index=False, floatfmt=".1f")
    
    with open(OUTPUT_REPORT, "w", encoding="utf-8") as f:
        f.write(summary_md)
        
    print("Report generated successfully.")

def main():
    A, X, emp_coefs, inc_coefs, sectors = load_data()
    
    results = {
        "base_jobs": None,
        "scenarios": {}
    }
    
    # Calculate Base Jobs once
    _, L_base = calculate_employment_impact(X, emp_coefs, 1.0)
    results["base_jobs"] = L_base
    
    for name, config in SCENARIOS.items():
        ratio = config["old"] / config["new"]
        desc = f"{config['old']}h -> {config['new']}h"
        
        print(f"Running Scenario: {name} ({desc}, Ratio: {ratio:.4f})")
        
        jobs_created, _ = calculate_employment_impact(X, emp_coefs, ratio)
        price_delta = calculate_price_impact(A, inc_coefs, ratio) # Pass full ratio (e.g. 1.10)
        
        results["scenarios"][name] = {
            "desc": desc,
            "ratio": ratio,
            "jobs_created": jobs_created,
            "price_delta": price_delta
        }
        
    generate_report(results, sectors)

if __name__ == "__main__":
    main()
