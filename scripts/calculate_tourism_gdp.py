import numpy as np

def get_tourism_gdp():
    # Load VAB for Rio de Janeiro (67 sectors)
    try:
        vab_rj = np.load(r'c:\Users\jonat\Documents\MIP e CGE\output\intermediary\VAB_Rio_de_Janeiro.npy')
    except FileNotFoundError:
        print("Arquivo VAB_Rio_de_Janeiro.npy não encontrado.")
        return

    # Mapeamento de setores característicos do turismo (Sectores 67 da MIP 2015 IBGE)
    # 45: Alojamento
    # 46: Alimentação
    # 39: Transporte terrestre (parte é turismo)
    # 41: Transporte aéreo (majoritariamente turismo)
    # 43: Agências de viagens e outros serviços de reserva
    # 64: Atividades artísticas, criativas e de espetáculos
    
    tourism_indices = {
        45: "Alojamento",
        46: "Alimentação",
        41: "Transporte Aéreo",
        43: "Agências de viagens",
        64: "Artes, cultura e lazer"
    }
    
    total_tourism_vab = 0
    print("VAB Setorial de Turismo - Rio de Janeiro (2021 Est.)")
    print("-" * 55)
    for idx, name in tourism_indices.items():
        if idx < len(vab_rj):
            val = vab_rj[idx]
            total_tourism_vab += val
            print(f"| {name:<25} | R$ {val:>10.2f} Mi |")
    
    pib_total_rj = vab_rj.sum()
    
    print("-" * 55)
    print(f"PIB Turismo Est. (Soma ACTs): R$ {total_tourism_vab:.2f} Mi")
    print(f"PIB Total RJ (Agregado VAB):  R$ {pib_total_rj:.2f} Mi")
    print(f"Participação no PIB Total:    {(total_tourism_vab/pib_total_rj)*100:.2f}%")

if __name__ == "__main__":
    get_tourism_gdp()
