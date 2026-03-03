
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

def generate_report_charts():
    print("=== GERANDO GRÁFICOS PARA NOTA TÉCNICA ===")
    
    # Load results
    with open('output/impacto_rock_in_rio_results.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    output_dir = 'output/report_assets'
    os.makedirs(output_dir, exist_ok=True)
    
    # Set style
    plt.style.use('seaborn-v0_8-muted')
    colors = ['#1a73e8', '#34a853', '#fbbc05', '#ea4335', '#673ab7', '#00bcd4']
    
    # 1. IMPACTO POR SETOR (Bar Chart)
    df_setores = pd.DataFrame(data['resumo_setorial'])
    df_setores = df_setores.sort_values('Impacto_Producao_MM', ascending=True)
    
    plt.figure(figsize=(10, 6))
    bars = plt.barh(df_setores['Setor'], df_setores['Impacto_Producao_MM'], color='#1a73e8')
    plt.title('Impacto na Produção por Grande Setor (R$ Milhões)', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('R$ Milhões', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Add values on bars
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 5, bar.get_y() + bar.get_height()/2, f'R$ {width:,.1f}', 
                 va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'impacto_setorial.png'), dpi=300)
    plt.close()

    # 2. COMPOSIÇÃO DO CHOQUE (Donut Chart)
    sections = ['Artes/Cultura', 'Alojamento', 'Alimentação', 'Comércio', 'Transporte', 'Outros']
    values = [40, 20, 15, 10, 10, 5]
    
    plt.figure(figsize=(8, 8))
    plt.pie(values, labels=sections, autopct='%1.1f%%', startangle=140, colors=colors, 
            wedgeprops={'width': 0.4, 'edgecolor': 'w'})
    plt.title('Distribuição do Gasto Inicial (Choque)', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'composicao_choque.png'), dpi=300)
    plt.close()

    # 3. RJ VS BRASIL (Spillover)
    labels = ['Rio de Janeiro (Local)', 'Resto do Brasil (Vazamento)']
    rj_impact = data['totais']['producao_total_rj']
    br_impact = data['totais']['vazamento_brasil']
    
    plt.figure(figsize=(8, 6))
    plt.bar(labels, [rj_impact, br_impact], color=['#1a73e8', '#34a853'])
    plt.title('Distribuição Geográfica do Impacto (R$ Milhões)', fontsize=14, fontweight='bold')
    plt.ylabel('R$ Milhões')
    
    for i, v in enumerate([rj_impact, br_impact]):
        plt.text(i, v + 20, f'R$ {v:,.1f}', ha='center', fontweight='bold')
        
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'geografia_impacto.png'), dpi=300)
    plt.close()

    print(f"\nSucesso! Gráficos salvos em {output_dir}")

if __name__ == "__main__":
    generate_report_charts()
