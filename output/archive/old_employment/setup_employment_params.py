import numpy as np
import os

def setup_employment():
    print("--- GERANDO PARÂMETROS DE EMPREGO (BENCHMARKS 2021) ---")
    inter_dir = 'output/intermediary'
    os.makedirs(inter_dir, exist_ok=True)
    
    # n = 67 setores (padrão da nossa MIP)
    e = np.zeros(67)
    
    # Coeficientes: Pessoas Ocupadas por R$ 1 Milhão de Produção (VBP)
    # Valores baseados em médias nacionais do IBGE (SCN 2021)
    
    # Agropecuária (Setores 0-12): Intensivo, mas mecanizado
    e[0:9].fill(12.0)   # Lavouras
    e[9:13].fill(10.0)  # Pecuária e Aves
    
    # Extração Mineral (Setores 15-19): Baixa intensidade (capital intensivo)
    e[15:20].fill(1.5)
    
    # Indústria de Transformação (Setores 20-39): Média intensidade
    # Nota: Refino (18) e Química (20-22) são bem baixos. Têxtil (14) é maior.
    e[20:37].fill(3.2)
    e[18] = 0.6  # Refino de Petróleo
    e[36] = 5.0  # Vestuário (Mais manual)
    
    # Serviços de Utilidade Pública (Setores 37-38)
    e[37:39].fill(1.8)
    
    # Construção (Setor 39)
    e[39] = 7.5
    
    # Comércio (Setor 40)
    e[40] = 9.0
    
    # Serviços (Setores 41-66)
    e[41:45].fill(5.5)  # Transportes
    e[45] = 11.0        # Alojamento (Muito intensivo)
    e[46] = 12.5        # Alimentação (Muito intensivo)
    e[47:51].fill(4.5)  # TI e Comunicação
    e[51] = 2.2         # Financeiro
    e[52] = 0.8         # Imobiliário (Baixo pessoal por real gerado) - aluguel
    e[53:59].fill(8.0)  # Serviços Profissionais e Administrativos
    e[59:61].fill(6.0)  # Adm Pública / Educação
    e[61] = 9.0         # Saúde Privada
    e[64] = 10.0        # Artes e Cultura
    e[66] = 15.0        # Serviços domésticos
    
    # Salvar
    np.save(os.path.join(inter_dir, 'employment_coefficients_2021.npy'), e)
    print(f"Arquivo salvo em {inter_dir}/employment_coefficients_2021.npy")
    print(f"Média do Coeficiente: {np.mean(e):.2f} pessoas/milhão")

if __name__ == "__main__":
    setup_employment()
