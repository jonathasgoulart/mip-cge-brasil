
import numpy as np
import os

def setup_employment_corrected():
    print("--- GERANDO PARÂMETROS DE EMPREGO (CORRIGIDOS 2021) ---")
    inter_dir = 'output/intermediary'
    os.makedirs(inter_dir, exist_ok=True)
    
    # n = 67 setores (0 a 66)
    e = np.zeros(67)
    
    # --- 1. AGROPECUÁRIA (0-2) ---
    e[0] = 13.0  # Agricultura
    e[1] = 11.0  # Pecuária
    e[2] = 14.0  # Produção florestal/Pesca
    
    # --- 2. EXTRAÇÃO (3-6) ---
    e[3] = 2.0   # Carvão
    e[4] = 0.3   # Petróleo e Gás (Altamente capital-intensivo)
    e[5] = 0.7   # Minério de Ferro (Mecanizado)
    e[6] = 1.1   # Outros Metais
    
    # --- 3. INDÚSTRIA DE TRANSFORMAÇÃO (7-36) ---
    e[7:10].fill(4.2)   # Alimentos
    e[10:12].fill(2.5)  # Bebidas e Fumo
    e[12] = 9.0         # Têxtil
    e[13] = 13.0        # Vestuário (Muito intensivo)
    e[14] = 11.0        # Calçados
    e[15:18].fill(4.5)  # Madeira, Papel, Impressão
    e[18] = 0.4         # Refino de Petróleo (Baixíssimo emprego/VBP)
    e[19] = 1.2         # Biocombustíveis
    e[20:23].fill(1.5)  # Químicos e Cosméticos
    e[23] = 2.2         # Farmacêuticos
    e[24:26].fill(3.5)  # Borracha, Plástico, Minerais não-metálicos
    e[26:28].fill(2.0)  # Siderurgia e Metalurgia
    e[28] = 4.0         # Prod. Metal
    e[29:31].fill(3.0)  # Eletrônicos e Maq Elétricas
    e[31] = 3.5         # Maq Mecânicas
    e[32:34].fill(2.8)  # Automotivo e Peças
    e[34] = 3.2         # Outros transp
    e[35] = 6.0         # Móveis
    e[36] = 7.0         # Manutenção
    
    # --- 4. UTILIDADES (37-38) ---
    e[37] = 1.1   # Energia
    e[38] = 2.5   # Água e Esgoto
    
    # --- 5. CONSTRUÇÃO (39) ---
    e[39] = 8.5
    
    # --- 6. COMÉRCIO (40) ---
    e[40] = 12.0
    
    # --- 7. SERVIÇOS (41-66) ---
    e[41:45].fill(5.5)  # Transportes
    e[45] = 14.0        # Alojamento (Intensivo)
    e[46] = 16.0        # Alimentação (Muito Intensivo)
    e[47:50].fill(3.8)  # Mídia e Telecom
    e[50] = 4.5         # TI
    e[51] = 1.8         # Financeiro
    e[52] = 0.4         # Imobiliário (Baixíssimo pessoal/VBP - Renda de Aluguel)
    e[53:59].fill(8.5)  # Profissionais e Apoio
    e[59] = 6.2         # Admin Pública
    e[60] = 7.5         # Educação Pública
    e[61] = 9.5         # Educação Privada
    e[62] = 8.0         # Saúde Pública
    e[63] = 11.0        # Saúde Privada
    e[64] = 12.0        # Artes
    e[65] = 9.0         # Organizações
    e[66] = 25.0        # Serviços domésticos (Baseado em VBP/VAB baixo e muita gente)
    
    # Salvar
    np.save(os.path.join(inter_dir, 'employment_coefficients_2021.npy'), e)
    print(f"Sucesso! {inter_dir}/employment_coefficients_2021.npy atualizado.")
    print(f"Coeficiente Médio: {np.mean(e):.2f} pessoas/milhão")
    print(f"Exemplo Ferro (Setor 5): {e[5]} (Anterior era 12.0!)")

if __name__ == "__main__":
    setup_employment_corrected()
