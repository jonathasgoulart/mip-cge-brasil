import numpy as np

# Coordenadas das Capitais (Lat, Lon)
# Fonte: Dados públicos aproximados dos centroides municipais das capitais
CAPITALS = {
    'RO': (-8.76194, -63.90389), # Porto Velho
    'AC': (-9.97538, -67.82492), # Rio Branco
    'AM': (-3.11903, -60.02173), # Manaus
    'RR': (2.82351, -60.67583),  # Boa Vista
    'PA': (-1.45575, -48.49018), # Belém
    'AP': (0.03557, -51.07053),  # Macapá
    'TO': (-10.1753, -48.3317),  # Palmas
    'MA': (-2.53073, -44.3068),  # São Luís
    'PI': (-5.09194, -42.8034),  # Teresina
    'CE': (-3.71722, -38.54306), # Fortaleza
    'RN': (-5.79448, -35.211),   # Natal
    'PB': (-7.11532, -34.861),   # João Pessoa
    'PE': (-8.05428, -34.8813),  # Recife
    'AL': (-9.66625, -35.7351),  # Maceió
    'SE': (-10.9472, -37.0731),  # Aracaju
    'BA': (-12.9774, -38.5023),  # Salvador
    'MG': (-19.9167, -43.9345),  # Belo Horizonte
    'ES': (-20.3155, -40.3128),  # Vitória
    'RJ': (-22.9068, -43.1729),  # Rio de Janeiro
    'SP': (-23.5505, -46.6333),  # São Paulo
    'PR': (-25.4284, -49.2733),  # Curitiba
    'SC': (-27.5954, -48.5480),  # Florianópolis
    'RS': (-30.0346, -51.2177),  # Porto Alegre
    'MS': (-20.4697, -54.6201),  # Campo Grande
    'MT': (-15.6014, -56.0979),  # Cuiabá
    'GO': (-16.6869, -49.2648),  # Goiânia
    'DF': (-15.7941, -47.8825)   # Brasília
}

UF_LIST = list(CAPITALS.keys())

def haversine(coord1, coord2):
    """Calcula distância em km entre duas coordenadas (lat, lon) usando Haversine."""
    R = 6371.0 # Raio da Terra em km
    
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R * c

def get_distance_matrix():
    """Retorna matriz de distâncias 27x27 (km) e lista ordenada de UFs."""
    n = len(UF_LIST)
    dist_mat = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            if i == j:
                # Distância interna (intra-regional)
                # Aproximação: 1/3 do raio de um círculo com a área da UF
                # Por simplicidade inicial, definimos uma distância mínima fixa
                dist_mat[i, j] = 50.0 
            else:
                dist_mat[i, j] = haversine(CAPITALS[UF_LIST[i]], CAPITALS[UF_LIST[j]])
                
    return dist_mat, UF_LIST

if __name__ == "__main__":
    d, ufs = get_distance_matrix()
    print("Matriz de Distâncias calculada.")
    print(f"Shape: {d.shape}")
    print(f"Distância SP-RJ: {d[ufs.index('SP'), ufs.index('RJ')]:.2f} km")
