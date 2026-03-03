
import pandas as pd
import numpy as np
import sys

# Ensure UTF-8 output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def audit_flows():
    print("=== AUDITORIA DETALHADA DE FLUXOS (Z) - MIP 2021 (PERFEITA) ===")
    file_path = 'output/Matriz_Nacional_2021_PERFEITA.xlsx'
    
    # Load Z and A
    df_z = pd.read_excel(file_path, sheet_name='Fluxos_Z_Nacionais', index_col=0)
    df_a = pd.read_excel(file_path, sheet_name='Coeficientes_A', index_col=0)
    
    sectors = df_z.columns.tolist()
    
    # 1. VERIFICAR CADEIAS CHAVE
    chains = [
        ("Agricultura", 0, "Alimentos", 9),
        ("Pecuária", 1, "Carnes", 7),
        ("Refino Petróleo", 18, "Transporte Terrestre", 41),
        ("Energia Elétrica", 37, "Indústria Metalúrgica", 26),
        ("Minério de Ferro", 5, "Siderurgia", 26),
        ("Construção", 39, "Produtos Minerais", 25) # Invertido: Construção compra de Minerais
    ]
    
    print("\n--- Verificação de Cadeias Produtivas (Fluxos Diretos) ---")
    for name_a, idx_a, name_b, idx_b in chains:
        flow = df_z.iloc[idx_a, idx_b]
        coeff = df_a.iloc[idx_a, idx_b]
        print(f"[{name_a}] -> [{name_b}]: R$ {flow:,.1f} M (Coef: {coeff:.4f})")

    # 2. TOP DEPENDÊNCIAS (Quem compra de quem?)
    print("\n--- Top 3 Insumos por Setor (Exemplos Selecionados) ---")
    select_sectors = [9, 13, 26, 39, 41, 51, 64] # Alimentos, VESTuario, Siderurgia, Construção, Transp, Finan, Artes
    for idx_b in select_sectors:
        sector_name = sectors[idx_b]
        col_data = df_z.iloc[:, idx_b].sort_values(ascending=False).head(4) # Pega 4 pra pular diagonal se for o caso
        total_in = col_sums = df_z.iloc[:, idx_b].sum()
        
        print(f"\nSetor Consumidor: {sector_name}")
        print(f"Total de Insumos: R$ {total_in:,.1f} M")
        for idx_a, val in col_data.items():
            pct = (val / total_in * 100) if total_in > 0 else 0
            print(f"  <- {idx_a[:30]}: {pct:.1f}% (R$ {val:,.1f} M)")

    # 3. VERIFICAR ANOMALIAS (Fluxos nulos onde deveria haver)
    # Ex: Transportes deveriam consumir Combustível (Refino)
    if df_z.iloc[18, 41] < 1:
        print("\nALERTA: Fluxo desprezível de Refino -> Transporte Terrestre!")
    
    # Ex: Agro deveria consumir Fertilizantes (Químicos 21)
    if df_z.iloc[21, 0] < 1:
        print("\nALERTA: Fluxo desprezível de Químicos -> Agro!")

    # 4. DIAGONAIS (Autoconsumo)
    print("\n--- Verificação de Autoconsumo (Diagonais Dominantes) ---")
    diagonals = np.diag(df_a.values)
    top_diag_idx = np.argsort(diagonals)[-5:][::-1]
    for idx in top_diag_idx:
        print(f"  {sectors[idx][:40]}: {diagonals[idx]*100:.1f}% da produção é autoconsumo")

if __name__ == "__main__":
    audit_flows()
