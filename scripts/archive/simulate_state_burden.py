
import json
import numpy as np
import csv

def run():
    print("=== SIMULANDO CARGA TRIBUTARIA POR ESTADO (ATUAL vs REFORMA) ===")
    
    # 1. Load Data
    path_vab = 'data/processed/2021_final/vab_regional.json'
    path_tax = 'data/processed/2021_final/tax_matrix.json'
    path_vab_nac = 'data/processed/2021_final/vab_nacional.npy'
    path_exports = 'data/processed/2021_final/export_ratios.json'
    
    with open(path_vab, 'r', encoding='utf-8') as f:
        vab_regional = json.load(f)
        
    with open(path_tax, 'r') as f:
        tax_data = json.load(f)
        
    vab_nacional = np.load(path_vab_nac)
    
    with open(path_exports, 'r') as f:
        export_ratios = json.load(f)
        
    # Calculate Effective Current Rates per Sector (67)
    # Rate = Tax / VAB
    total_tax_vec = np.zeros(67)
    tax_source = tax_data.get('taxes_by_type', tax_data)
    for k, v in tax_source.items():
        if not isinstance(v, list): continue
        if k == 'metadata': continue
        if k == 'II': continue # Import Tax not relevant for domestic burden comparison?
                               # Actually, II is paid by importer. It burdens the sector INPUTS.
                               # But here we measure burden ON the sector's VAB.
                               # Usually II is excluded from "Carga sobre Producao Domestica".
        total_tax_vec += np.array(v, dtype=float)
        
    current_rates = np.zeros(67)
    for i in range(67):
        if vab_nacional[i] > 0:
            current_rates[i] = total_tax_vec[i] / vab_nacional[i]
            
    # Reform Parameters
    STANDARD_RATE = 0.1827 # 18.27%
    
    # Exemption Factors (0.0 = Full Tax, 0.4 = 60% reduction)
    # Standard: 1.0
    factors = np.ones(67)
    
    # Agro (1,2,3) -> 0.4
    factors[0] = 0.4
    factors[1] = 0.4
    factors[2] = 0.4 
    
    # Health/Edu (61,62,63,64) -> 0.4 (Private Only?)
    factors[61] = 0.4 # Edu Priv
    factors[63] = 0.4 # Health Priv
    
    # Construction (39) -> often special regime. Let's assume standard (1.0) or deducoes (0.6)?
    factors[39] = 1.0 
    
    # Calculate Burdens per State
    print(f"{'UF':<5} | {'VAB (Bi)':<10} | {'Atual %':<10} | {'Reforma %':<10} | {'Delta':<10}")
    print("-" * 60)
    
    results = []
    
    for state, sector_dict in vab_regional.items():
        # Reconstruct sector vector for state (dictionary to array)
        # sector_dict is likely already 67-vector (list) from my rebuild script?
        # Rebuild script saved "final_vab_matrix[state] = new_vec_67.tolist()"
        # So sector_dict is just a LIST of 67 floats.
        
        state_vab_vec = np.array(sector_dict)
        total_vab_state = sum(state_vab_vec)
        
        # A. Current Burden (Estimate)
        # Sum(VAB_i * CurrentRate_i)
        current_tax_state = sum(state_vab_vec * current_rates)
        current_burden_pct = (current_tax_state / total_vab_state) * 100
        
        # B. Reform Burden
        # Sum(VAB_i * StandardRate * Factor_i * (1 - ExportRatio_i))
        # Logic: Exports are zero rated.
        reform_tax_state = 0.0
        for i in range(67):
            taxable_base = state_vab_vec[i] * (1.0 - export_ratios[i])
            reform_tax_state += taxable_base * STANDARD_RATE * factors[i]
            
        reform_burden_pct = (reform_tax_state / total_vab_state) * 100
        
        delta = reform_burden_pct - current_burden_pct
        
        results.append({
            "UF": state,
            "VAB": total_vab_state,
            "Current": current_burden_pct,
            "Reform": reform_burden_pct,
            "Delta": delta
        })
        
    # Sort by Delta (Winners to Losers)
    results.sort(key=lambda x: x['Delta'])
    
    # Generate Markdown Report
    md_path = 'output/relatorio_impacto_regional.md'
    csv_path = 'output/impacto_regional.csv' # For CSV output
    
    # Identify Dominant Sector (Driver)
    # Simple heuristic: Max share among Agro, Ind, Serv
    # Ind Indices: 3..39
    # Agro Indices: 0..2
    # Serv Indices: 40..66
    
    with open(md_path, 'w', encoding='utf-8') as f, open(csv_path, 'w', encoding='utf-8', newline='') as f_csv:
        writer = csv.writer(f_csv)
        writer.writerow(['UF', 'VAB (Bi)', 'Carga Atual (%)', 'Carga Reforma (%)', 'Delta (pp)', 'Setor Dominante'])
        
        f.write("# Relatório de Impacto Regional: Reforma Tributária\n\n")
        f.write("**Cenário:** Alíquota Padrão 18.27% | Descontos: Agro/Saúde/Edu (60%) | Exportação (0%)\n\n")
        f.write("| UF | VAB (R$ Bi) | Carga Atual | Carga Reforma | Variação (pp) | Perfil Econômico |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :--- |\n")
        
        for r in results:
            state = r['UF']
            # Get sector breakdown
            if state in vab_regional:
                vec = np.array(vab_regional[state])
            else:
                vec = np.zeros(67)
                
            total = sum(vec)
            if total > 0:
                share_agro = sum(vec[0:3]) / total
                share_ind = sum(vec[3:40]) / total
                share_serv = sum(vec[40:67]) / total
                
                # Classification
                if share_ind > 0.25: profile = "Industrial" # Lower threshold because services dominate everywhere
                if share_agro > 0.20: profile = "Agroindústria"
                if share_serv > 0.75: profile = "Serviços/Pub"
                
                # Refined winner
                best = max(share_agro, share_ind, share_serv)
                if best == share_agro: profile = f"Agro ({share_agro:.0%})"
                elif best == share_ind: profile = f"Ind ({share_ind:.0%})"
                else: profile = f"Serv ({share_serv:.0%})"
                
                # Adjust label for specific cases
                if share_ind > 0.30: profile = f"**Industrial** ({share_ind:.0%})"
                if share_agro > 0.30: profile = f"**Agro** ({share_agro:.0%})"
            else:
                profile = "N/A"
            
            # Sanitize UF for printing if needed, usually file write handles utf-8 fine
            
            line = f"| **{state}** | {r['VAB']/1e3:,.1f} | {r['Current']:.2f}% | {r['Reform']:.2f}% | **{r['Delta']:+.2f}** | {profile} |\n"
            f.write(line)
            
            writer.writerow([state, f"{r['VAB']/1e3:.1f}", f"{r['Current']:.2f}", f"{r['Reform']:.2f}", f"{r['Delta']:.2f}", profile.replace('*','')])
            
    print(f"Report generated: {md_path}")
    print(f"CSV generated: {csv_path}")

if __name__ == "__main__":
    run()
