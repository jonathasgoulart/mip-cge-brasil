from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
import os
import json
from fastapi.middleware.cors import CORSMiddleware

from .simulators.demand_shock import run_demand_shock, AGGREGATION_LEVELS
from .simulators.tax_reform import run_tax_reform
from .simulators.labor_policy import run_labor_policy

app = FastAPI(title="MIP-CGE Brasil Simulation API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded sector labels with Unicode Escapes to be 100% Mojibake-proof
# u00e0 = à, u00e1 = á, u00e2 = â, u00e3 = ã, u00e7 = ç, u00e9 = é, u00ea = ê, u00ed = í, u00f3 = ó, u00f4 = ô, u00fa = ú
DETAILED_SECTORS = [
    "Agricultura, inclusive o apoio \u00e0 agricultura e a p\u00f3s-colheita",
    "Pecu\u00e1ria, inclusive o apoio \u00e0 pecu\u00e1ria",
    "Produ\u00e7\u00e3o florestal; pesca e aquicultura",
    "Extra\u00e7\u00e3o de carv\u00e3o mineral e de minerais n\u00e3o met\u00e1licos",
    "Extra\u00e7\u00e3o de petr\u00f3leo e g\u00e1s, inclusive as atividades de apoio",
    "Extra\u00e7\u00e3o de min\u00e9rio de ferro, inclusive beneficiamentos e a aglomera\u00e7\u00e3o",
    "Extra\u00e7\u00e3o de minerais met\u00e1licos n\u00e3o ferrosos, inclusive beneficiamentos",
    "Abate e produtos de carne, inclusive os produtos do latic\u00ednio e da pesca",
    "Fabrica\u00e7\u00e3o e refino de a\u00e7\u00facar",
    "Outros produtos alimentares",
    "Fabrica\u00e7\u00e3o de bebidas",
    "Fabrica\u00e7\u00e3o de produtos do fumo",
    "Fabrica\u00e7\u00e3o de produtos t\u00eaxteis",
    "Confec\u00e7\u00e3o de artefatos do vestu\u00e1rio e acess\u00f3rios",
    "Fabrica\u00e7\u00e3o de cal\u00e7ados e de artefatos de couro",
    "Fabrica\u00e7\u00e3o de produtos da madeira",
    "Fabrica\u00e7\u00e3o de celulose, papel e produtos de papel",
    "Impress\u00e3o e reprodu\u00e7\u00e3o de grava\u00e7\u00f5es",
    "Refino de petr\u00f3leo e coquerias",
    "Fabrica\u00e7\u00e3o de biocombust\u00edveis",
    "Fabrica\u00e7\u00e3o de qu\u00edmicos org\u00e2nicos e inorg\u00e2nicos, resinas e elast\u00f4meros",
    "Fabrica\u00e7\u00e3o de defensivos, desinfestantes, tintas e qu\u00edmicos diversos",
    "Fabrica\u00e7\u00e3o de produtos de limpeza, cosm\u00e9ticos/perfumaria e higiene pessoal",
    "Fabrica\u00e7\u00e3o de produtos farmoqu\u00edmicos e farmac\u00eauticos",
    "Fabrica\u00e7\u00e3o de produtos de borracha e de material pl\u00e1stico",
    "Fabrica\u00e7\u00e3o de produtos de minerais n\u00e3o met\u00e1licos",
    "Produ\u00e7\u00e3o de ferro gusa/ferroligas, siderurgia e tubos de a\u00e7o sem costura",
    "Metalurgia de metais n\u00e3o ferosos e a fundi\u00e7\u00e3o de metais",
    "Fabrica\u00e7\u00e3o de produtos de metal, exceto m\u00e1quinas e equipamentos",
    "Fabrica\u00e7\u00e3o de equipamentos de inform\u00e1tica, produtos eletr\u00f4nicos e \u00f3pticos",
    "Fabrica\u00e7\u00e3o de m\u00e1quinas e equipamentos el\u00e9tricos",
    "Fabrica\u00e7\u00e3o de m\u00e1quinas e equipamentos mec\u00e2nicos",
    "Fabrica\u00e7\u00e3o de autom\u00f3veis, caminh\u00f5es e \u00f4nibus, exceto pe\u00e7as",
    "Fabrica\u00e7\u00e3o de pe\u00e7as e acess\u00f3rios para ve\u00edculos automotores",
    "Fabrica\u00e7\u00e3o de outros equipamentos de transporte, exceto ve\u00edculos automotores",
    "Fabrica\u00e7\u00e3o de m\u00f3veis e de produtos de ind\u00fastrias diversas",
    "Manuten\u00e7\u00e3o, repara\u00e7\u00e3o e instala\u00e7\u00e3o de m\u00e1quinas e equipamentos",
    "Energia el\u00e9trica, g\u00e1s natural e outras utilidades",
    "\u00c1gua, esgoto e gest\u00e3o de res\u00edduos",
    "Constru\u00e7\u00e3o",
    "Com\u00e9rcio por atacado e varejo",
    "Transporte terrestre",
    "Transporte aquavi\u00e1rio",
    "Transporte a\u00e9reo",
    "Armazenamento, atividades auxiliares dos transportes e correio",
    "Alojamento",
    "Alimenta\u00e7\u00e3o",
    "Edi\u00e7\u00e3o e edi\u00e7\u00e3o integrada \u00e0 impress\u00e3o",
    "Atividades de televis\u00e3o, r\u00e1dio, cinema e grava\u00e7\u00e3o/edi\u00e7\u00e3o de som e imagem",
    "Telecomunica\u00e7\u00f5es",
    "Desenvolvimento de sistemas e outros servi\u00e7os de informa\u00e7\u00e3o",
    "Intermedia\u00e7\u00e3o financeira, seguros e previd\u00eancia complementar",
    "Atividades imobili\u00e1rias",
    "Atividades jur\u00eddicas, cont\u00e1beis, consultoria e sedes de empresas",
    "Servi\u00e7os de arquitetura, engenharia, testes/an\u00e1lises t\u00e9cnicas e P & D",
    "Outras atividades profissionais, cient\u00edficas e t\u00e9cnicas",
    "Alugu\u00e9is n\u00e3o imobili\u00e1rios e gest\u00e3o de ativos de propriedade intelectual",
    "Outras atividades administrativas e servi\u00e7os complementares",
    "Atividades de vigil\u00e2ncia, seguran\u00e7a e investiga\u00e7\u00e3o",
    "Administra\u00e7\u00e3o p\u00fablica, defesa e seguridade social",
    "Educa\u00e7\u00e3o p\u00fablica",
    "Educa\u00e7\u00e3o privada",
    "Sa\u00fade p\u00fablica",
    "Sa\u00fade privada",
    "Atividades art\u00edsticas, criativas e de espet\u00e1culos",
    "Organiza\u00e7\u00f5es associativas e outros servi\u00e7os pessoais",
    "Servi\u00e7os dom\u00e9sticos"
]

class ShockRequest(BaseModel):
    region: str
    shocks: Dict[str, float]
    aggregation_level: str = "detailed"
    require_spillover: bool = False

@app.get("/")
async def root():
    return {"message": "MIP-CGE Brasil API is running"}

@app.post("/simulate/demand")
async def simulate_demand(request: ShockRequest):
    try:
        return run_demand_shock(
            request.region, 
            request.shocks, 
            request.aggregation_level,
            request.require_spillover
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/export/excel")
async def export_excel(results: Dict[str, Any]):
    try:
        from .simulators.demand_shock import export_to_excel
        from fastapi.responses import StreamingResponse
        
        output = export_to_excel(results)
        return StreamingResponse(
            output,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=resultado_simulacao.xlsx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metadata/sectors")
async def get_sectors(level: str = "detailed"):
    level = level.lower()
    if level in AGGREGATION_LEVELS:
        return [{"id": name, "name": name} for _, _, name in AGGREGATION_LEVELS[level]]
    
    return [{"id": str(i), "name": name} for i, name in enumerate(DETAILED_SECTORS)]

@app.get("/metadata/regions")
async def get_regions():
    return ["RO", "AC", "AM", "RR", "PA", "AP", "TO", "MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA", "MG", "ES", "RJ", "SP", "PR", "SC", "RS", "MS", "MT", "GO", "DF", "Nacional"]
