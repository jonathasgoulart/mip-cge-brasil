"""
Gera um relatorio HTML interativo e detalhado
para o estudo da Economia Criativa do Rio de Janeiro.
"""
import json
import os
from pathlib import Path

BASE_DIR = Path(r'C:\Users\jonat\Documents\MIP e CGE')
OUTPUT_DIR = BASE_DIR / 'output'

def format_currency(value):
    return f"R$ {value:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_number(value):
    return f"{value:,.0f}".replace(",", ".")

def generate_html(data):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estudo de Impacto: Economia Criativa do Rio de Janeiro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #1e293b; }}
        .card {{ background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); padding: 24px; margin-bottom: 24px; }}
        h1 {{ background: linear-gradient(135deg, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .gradient-bg {{ background: linear-gradient(135deg, #1e40af, #4c1d95); color: white; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 16px; margin-bottom: 16px; }}
        th {{ background-color: #f1f5f9; text-align: left; padding: 12px 16px; font-weight: 600; border-bottom: 2px solid #e2e8f0; font-size: 0.875rem; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }}
        td {{ padding: 12px 16px; border-bottom: 1px solid #e2e8f0; font-size: 0.9rem; }}
        tr:hover td {{ background-color: #f8fafc; }}
        .number-col {{ text-align: right; font-variant-numeric: tabular-nums; }}
        .badge-creative {{ background-color: #dbeafe; color: #1e40af; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }}
        .badge-noncreative {{ background-color: #f1f5f9; color: #475569; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; font-weight: 600; }}
    </style>
</head>
<body class="p-8 max-w-7xl mx-auto">
    
    <header class="text-center mb-12">
        <h1 class="text-4xl font-bold mb-4">Impacto Econômico da Economia Criativa no Rio de Janeiro</h1>
        <p class="text-xl text-slate-600 max-w-3xl mx-auto">Análise de Insumo-Produto Multi-Regional (MRIO v4 2021) com calibração econométrica (Modelagem Gravitacional e Coeficientes FLQ). Avaliação do efeito multiplicador de grandes eventos e transbordamentos estaduais e intra-setoriais.</p>
    </header>

"""
    
    # 1. Macro Context (if available in estudo_central)
    if 'estudo_central' in data:
        central = data['estudo_central']
        html += f"""
    <div class="card gradient-bg mb-8">
        <h2 class="text-2xl font-bold mb-6 border-b border-white/20 pb-2">Panorama Macroestrutural (Matriz 67x67 RJ)</h2>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div>
                <p class="text-indigo-200 text-sm font-semibold uppercase tracking-wider mb-1">VAB Criativo (RJ)</p>
                <p class="text-3xl font-bold">R$ 157,0 Bi</p>
                <p class="text-sm mt-1 text-indigo-100">10,0% do PIB Estadual</p>
            </div>
            <div>
                <p class="text-indigo-200 text-sm font-semibold uppercase tracking-wider mb-1">Especialização (LQ)</p>
                <p class="text-3xl font-bold">1,16</p>
                <p class="text-sm mt-1 text-indigo-100">Vantagem comparativa latente</p>
            </div>
            <div>
                <p class="text-indigo-200 text-sm font-semibold uppercase tracking-wider mb-1">Multiplicador Médio</p>
                <p class="text-3xl font-bold">1,48x</p>
                <p class="text-sm mt-1 text-indigo-100">R$1 de demanda = R$1,48 de VBP</p>
            </div>
            <div>
                <p class="text-indigo-200 text-sm font-semibold uppercase tracking-wider mb-1">Spillover Nao-Criativo</p>
                <p class="text-3xl font-bold">22,7%</p>
                <p class="text-sm mt-1 text-indigo-100">Vazamento inter-setorial</p>
            </div>
        </div>
    </div>
"""

    html += """
    <h2 class="text-3xl font-bold mb-6 mt-12 text-slate-800 border-b-2 border-indigo-500 pb-2 inline-block">Raio-X da Economia Criativa do RJ</h2>
    <p class="text-slate-600 mb-8 max-w-4xl">O ecossistema criativo fluminense é heterogêneo. A tabela abaixo detalha o perfil econômico e inter-setorial de cada sub-segmento, evidenciando o Valor Adicionado Bruto (VAB), a especialização local (Location Quotient > 1 indica vantagem comparativa face ao resto do Brasil) e as métricas de encadeamento.</p>

    <div class="overflow-x-auto mb-12">
        <table>
            <thead>
                <tr>
                    <th>Segmento Criativo</th>
                    <th class="number-col">VAB (R$ Mi)</th>
                    <th class="number-col">Especialização (LQ)</th>
                    <th class="number-col">Mult. de Produção</th>
                    <th class="number-col">Mult. de Emprego</th>
                    <th class="number-col">Empregos Totais base</th>
                </tr>
            </thead>
            <tbody>
"""
    if 'estudo_central' in data:
        ctx = data['estudo_central']['contexto']['segmentos']
        mults = data['estudo_central']['multiplicadores']['por_segmento']
        emps = data['estudo_central']['emprego']['por_segmento']
        
        # Sort by VAB
        sorted_segs = sorted(ctx.items(), key=lambda x: x[1]['vab_rj_mi'], reverse=True)
        for seg_name, seg_data in sorted_segs:
            lq = seg_data['location_quotient']
            lq_class = "text-green-600 font-bold" if lq > 1.1 else ("text-blue-600 font-semibold" if lq > 1.0 else "text-slate-500")
            m_prod = mults[seg_name]['multiplicador_producao']
            m_emp = emps[seg_name]['multiplicador_emprego']
            emp_tot = emps[seg_name]['emprego_total']
            
            html += f"""
                <tr>
                    <td class="font-medium text-slate-700">{seg_name}</td>
                    <td class="number-col">{format_currency(seg_data['vab_rj_mi'])}</td>
                    <td class="number-col {lq_class}">{lq:.2f}</td>
                    <td class="number-col text-slate-600">{m_prod:.2f}x</td>
                    <td class="number-col text-slate-600">{m_emp:.2f}x</td>
                    <td class="number-col text-slate-600">{format_number(emp_tot)}</td>
                </tr>
"""

    html += """
            </tbody>
        </table>
    </div>

    <h2 class="text-3xl font-bold mb-6 mt-12 text-slate-800 border-b-2 border-indigo-500 pb-2 inline-block">Estudos de Caso: Choques Exógenos de Demanda Final</h2>
    <p class="text-slate-600 mb-8 max-w-4xl">Simulações de impacto econômico (efeitos diretos e indiretos via Inversa de Leontief) para eventos reais, incorporando vetores de demanda parametrizados para 67 setores. Vazamentos inter-regionais calculados utilizando coeficientes de comércio (Trade Probabilities) do modelo gravitacional calibrado (MRIO).</p>
"""

    # 2. Iterate over Events
    events = [k for k in data.keys() if k != 'estudo_central']
    for idx, event_name in enumerate(events):
        ev = data[event_name]
        
        html += f"""
    <div class="card">
        <div class="flex items-center justify-between mb-6">
            <h3 class="text-2xl font-bold text-slate-800">{event_name}</h3>
            <span class="bg-indigo-100 text-indigo-800 text-sm font-semibold px-3 py-1 rounded-full">{ev['descricao']}</span>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div class="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <p class="text-slate-500 text-xs font-semibold uppercase tracking-wider mb-1">Choque de Demanda F</p>
                <p class="text-2xl font-bold text-slate-800">{format_currency(ev['choque_total'])} Mi</p>
                <p class="text-xs text-slate-500 mt-1">({ev.get('pct_criativo_choque', 0):.1f}% direcionado a setores criativos)</p>
            </div>
            <div class="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p class="text-blue-600 text-xs font-semibold uppercase tracking-wider mb-1">Produção Total (Brasil)</p>
                <p class="text-2xl font-bold text-blue-900">{format_currency(ev['producao_total_brasil'])} Mi</p>
                <p class="text-xs text-blue-700 mt-1">Multiplicador: {ev['multiplicador_brasil']:.3f}x</p>
            </div>
            <div class="bg-green-50 p-4 rounded-lg border border-green-200">
                <p class="text-green-600 text-xs font-semibold uppercase tracking-wider mb-1">Empregos Totais Gerados</p>
                <p class="text-2xl font-bold text-green-900">{format_number(ev['empregos_total_brasil'])}</p>
                <p class="text-xs text-green-700 mt-1">{(ev['empregos_total_brasil']/(ev['choque_total']/1000)):,.0f} vagas por R$ 1 Bi</p>
            </div>
            <div class="bg-amber-50 p-4 rounded-lg border border-amber-200">
                <p class="text-amber-600 text-xs font-semibold uppercase tracking-wider mb-1">Arrecadação RJ (ICMS+ISS)</p>
                <p class="text-2xl font-bold text-amber-900">{format_currency(ev['fiscal_rj'])} Mi</p>
                <p class="text-xs text-amber-700 mt-1">{ev['fiscal_rj']/ev['choque_total']*100:.1f}% do choque (Retorno Tácito)</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <!-- Col 1: Spillovers Nacionais -->
            <div>
                <h4 class="text-lg font-semibold mb-4 text-slate-700">Vazamento Inter-regional (Spillovers de Demanda)</h4>
                <p class="text-sm text-slate-600 mb-4">A demanda gerada no RJ ativa cadeias produtivas globais, exigindo importações intermediárias de outros estados. O MRIO captura o fluxo reverso onde R$ {format_currency(ev['producao_outros_estados'])} Mi ({ev['producao_outros_estados']/ev['producao_total_brasil']*100:.1f}%) vazam para o resto do Brasil.</p>
                
                <div style="height: 300px;">
                    <canvas id="chartSpillover_{idx}"></canvas>
                </div>
            </div>

            <!-- Col 2: Segmentos Criativos -->
            <div>
                <h4 class="text-lg font-semibold mb-4 text-slate-700">Decomposição por Segmento Criativo</h4>
                <p class="text-sm text-slate-600 mb-4">A captação local de valor varia por sub-segmento da economia criativa consoante as suas ligações inter-industriais (backward/forward linkages).</p>
                
                <table>
                    <thead>
                        <tr>
                            <th>Segmento Criativo</th>
                            <th class="number-col">VBP Gerado (R$ Mi)</th>
                            <th class="number-col">Empregos</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        seg_data = ev['segmentos_criativos']
        seg_labels = list(seg_data.keys())
        seg_prods = [seg_data[k]['producao'] for k in seg_labels]
        
        for k, v in sorted(seg_data.items(), key=lambda item: item[1]['producao'], reverse=True):
            html += f"""
                        <tr>
                            <td class="font-medium text-slate-700">{k}</td>
                            <td class="number-col text-slate-600">{format_currency(v['producao'])}</td>
                            <td class="number-col text-slate-600">{format_number(v['empregos'])}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mb-8 bg-slate-50 border border-slate-200 rounded-lg p-5">
            <h4 class="text-lg font-semibold mb-2 text-slate-800">Premissas do Choque (Vetor de Demanda Final)</h4>
            <p class="text-sm text-slate-600 mb-4">Como a injeção monetária do evento foi alocada na matriz insumo-produto. Esta distribuição reflete o perfil estimado de gastos (turistas, infraestrutura, cachês e organização).</p>
            <div class="overflow-x-auto">
                <table class="mb-0">
                    <thead>
                        <tr>
                            <th class="bg-slate-100">Setor Padrão IBGE</th>
                            <th class="bg-slate-100 number-col">Choque Direto (R$ Mi)</th>
                            <th class="bg-slate-100 number-col">% do Total</th>
                            <th class="bg-slate-100 text-center">Classificação</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        shock_sectors = [s for s in ev['setores_detalhados_rj'] if s.get('choque_direto', 0) > 0]
        shock_sectors.sort(key=lambda x: x['choque_direto'], reverse=True)
        for s in shock_sectors:
            badge = '<span class="badge-creative">Criativo</span>' if s['criativo'] else '<span class="badge-noncreative">Não-Criativo</span>'
            pct_choque = s['choque_direto'] / ev['choque_total'] * 100
            str_pct = f"{pct_choque:.1f}%"
            html += f"""
                        <tr>
                            <td class="font-medium text-slate-700">{s['setor']}</td>
                            <td class="number-col text-slate-800 font-bold">{format_currency(s['choque_direto'])}</td>
                            <td class="number-col text-slate-500">{str_pct}</td>
                            <td class="text-center">{badge}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
        </div>

        <div>
            <h4 class="text-lg font-semibold mb-2 text-slate-700">Top Setores Nao-Criativos Beneficiados (Efeito Indireto)</h4>
            <p class="text-sm text-slate-600 mb-4">Setores que recebem os maiores transbordamentos intersetoriais de demanda induzida, sem pertencerem primariamente à classificação de economia criativa (CNAEs selecionados).</p>
            <div class="overflow-x-auto">
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Setor MIP (IBGE)</th>
                            <th class="number-col">Incremento no VBP (R$ Mi)</th>
                            <th class="number-col">Novos Empregos</th>
                            <th class="number-col">Arrecadação ICMS/ISS (R$ Mi)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        top_nc = ev['setores_nao_criativos_rj'][:10]
        for i, s in enumerate(top_nc):
            html += f"""
                        <tr>
                            <td class="text-slate-500 font-medium">#{i+1}</td>
                            <td class="font-medium text-slate-700">{s['setor']}</td>
                            <td class="number-col text-indigo-600 font-medium">{format_currency(s['producao'])}</td>
                            <td class="number-col text-slate-600">{format_number(s['empregos'])}</td>
                            <td class="number-col text-slate-600">{format_currency(s['icms']+s['iss'])}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </div>
        </div>
    </div>
"""

        # Prepare chart data
        spillover_states = ev['spillover_por_estado']
        # Filter top 5 (exclude RJ which is #1 usually, but let's check)
        states_only = [s for s in spillover_states if s['uf'] != 'RJ'][:6]
        states_labels = [s['uf'] for s in states_only]
        states_prods = [s['producao'] for s in states_only]
        
        html += f"""
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            const ctx_{idx} = document.getElementById('chartSpillover_{idx}').getContext('2d');
            new Chart(ctx_{idx}, {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(states_labels)},
                    datasets: [{{
                        label: 'VBP Gerado (Transbordamento p/ outros Estados)',
                        data: {json.dumps(states_prods)},
                        backgroundColor: '#3b82f6',
                        borderRadius: 4
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }},
                    scales: {{
                        y: {{ beginAtZero: true, grid: {{ borderDash: [2, 4] }} }}
                    }}
                }}
            }});
        }});
    </script>
"""

    html += """
    <footer class="mt-12 pt-6 border-t border-slate-200 text-slate-500 text-sm flex justify-between">
        <p>Modelo CGE-MIP Brasil - Calibrado 2021</p>
        <p>Base Matemática: Inversa de Leontief, Ajuste FLQ Regional, Modelo Gravitacional Inter-Regional (Haversine)</p>
    </footer>
</body>
</html>
"""
    
    out_path = OUTPUT_DIR / 'relatorio_final_economia_criativa.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Relatório HTML salvo em: {out_path}")

if __name__ == "__main__":
    with open(OUTPUT_DIR / 'relatorio_economia_criativa_completo.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    generate_html(data)
