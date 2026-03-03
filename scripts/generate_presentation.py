"""
Gera uma apresentação interativa (Reveal.js) baseada nos dados do estudo
da Economia Criativa do Rio de Janeiro.
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

def generate_presentation(data):
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Apresentação: Economia Criativa RJ</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reset.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/theme/white.min.css" id="theme">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .reveal {{ font-family: 'Inter', sans-serif; }}
        .reveal h1, .reveal h2, .reveal h3, .reveal h4 {{ font-family: 'Inter', sans-serif; text-transform: none; color: #1e293b; font-weight: 700; }}
        .reveal section img {{ border: none; box-shadow: none; margin: 0; }}
        .gradient-text {{ background: linear-gradient(135deg, #2563eb, #7c3aed); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .slide-bg-blue {{ background: linear-gradient(135deg, #1e40af, #4c1d95); }}
        .reveal .slide-background.slide-bg-blue {{ background: linear-gradient(135deg, #1e40af, #4c1d95); }}
        .box-stat {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin: 8px; flex: 1; }}
        .box-title {{ font-size: 0.8em; color: #64748b; font-weight: 600; text-transform: uppercase; margin-bottom: 8px; }}
        .box-value {{ font-size: 1.8em; color: #0f172a; font-weight: bold; margin-bottom: 0; }}
        .box-desc {{ font-size: 0.7em; color: #64748b; margin-top: 4px; }}
        .creative-table {{ width: 100%; font-size: 0.6em; border-collapse: collapse; margin-top: 20px; }}
        .creative-table th {{ background: #f1f5f9; padding: 12px; text-align: left; border-bottom: 2px solid #cbd5e1; color: #334155; }}
        .creative-table td {{ padding: 10px 12px; border-bottom: 1px solid #e2e8f0; color: #475569; }}
        .num-col {{ text-align: right !important; font-variant-numeric: tabular-nums; }}
        .flex-row {{ display: flex; flex-direction: row; gap: 16px; justify-content: center; align-items: stretch; width: 100%; }}
        .flex-col {{ display: flex; flex-direction: column; width: 50%; justify-content: flex-start; align-items: stretch; }}
        .chart-container {{ height: 350px; width: 100%; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            
            <!-- Slide 1: Capa -->
            <section>
                <h1 class="gradient-text" style="font-size: 2.2em; margin-bottom: 1em;">Impacto Econômico da<br>Economia Criativa no Rio de Janeiro</h1>
                <p style="font-size: 0.9em; color: #64748b;">Análise de Insumo-Produto Multi-Regional (MRIO v4 2021)</p>
                <p style="font-size: 0.7em; color: #94a3b8; margin-top: 2em;">Utilize as setas do teclado para navegar</p>
            </section>
"""

    if 'estudo_central' in data:
        # Slide 2: Panorama Macro
        html += f"""
            <!-- Slide 2: Panorama -->
            <section data-state="slide-bg-blue" data-background-color="#1e3a8a">
                <h2 style="color: white; font-size: 1.6em; margin-bottom: 1.5em;">Panorama Macroestrutural (RJ)</h2>
                <div class="flex-row">
                    <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 20px; flex: 1;">
                        <p style="color: #93c5fd; font-size: 0.7em; font-weight: 600; text-transform: uppercase;">VAB Criativo (RJ)</p>
                        <p style="color: white; font-size: 2em; font-weight: bold; margin: 0;">R$ 157,0 Bi</p>
                        <p style="color: #bfdbfe; font-size: 0.8em; margin-top: 8px;">10,0% do PIB Estadual</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 20px; flex: 1;">
                        <p style="color: #93c5fd; font-size: 0.7em; font-weight: 600; text-transform: uppercase;">Especialização (LQ)</p>
                        <p style="color: white; font-size: 2em; font-weight: bold; margin: 0;">1,16</p>
                        <p style="color: #bfdbfe; font-size: 0.8em; margin-top: 8px;">Vantagem comparativa</p>
                    </div>
                </div>
                <div class="flex-row" style="margin-top: 20px;">
                    <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 20px; flex: 1;">
                        <p style="color: #93c5fd; font-size: 0.7em; font-weight: 600; text-transform: uppercase;">Multiplicador Médio</p>
                        <p style="color: white; font-size: 2em; font-weight: bold; margin: 0;">1,48x</p>
                        <p style="color: #bfdbfe; font-size: 0.8em; margin-top: 8px;">R$1 demanda = R$1,48 VBP</p>
                    </div>
                    <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 20px; flex: 1;">
                        <p style="color: #93c5fd; font-size: 0.7em; font-weight: 600; text-transform: uppercase;">Spillover Não-Criativo</p>
                        <p style="color: white; font-size: 2em; font-weight: bold; margin: 0;">22,7%</p>
                        <p style="color: #bfdbfe; font-size: 0.8em; margin-top: 8px;">Vazamento para outros setores</p>
                    </div>
                </div>
            </section>
"""

        # Slide 3: Raio-X Sub-setorial
        ctx = data['estudo_central']['contexto']['segmentos']
        mults = data['estudo_central']['multiplicadores']['por_segmento']
        sorted_segs = sorted(ctx.items(), key=lambda x: x[1]['vab_rj_mi'], reverse=True)
        
        html += """
            <!-- Slide 3: Raio-X -->
            <section>
                <h2 style="font-size: 1.4em;">Raio-X da Economia Criativa</h2>
                <table class="creative-table">
                    <thead>
                        <tr>
                            <th>Segmento</th>
                            <th class="num-col">VAB (R$ Mi)</th>
                            <th class="num-col">Espec. (LQ)</th>
                            <th class="num-col">Mult. de Produção</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        for seg_name, seg_data in sorted_segs:
            lq = seg_data['location_quotient']
            color = "#16a34a" if lq > 1.1 else ("#2563eb" if lq > 1.0 else "#64748b")
            bold = "font-weight: bold;" if lq > 1.0 else ""
            m_prod = mults[seg_name]['multiplicador_producao']
            html += f"""
                        <tr>
                            <td style="font-weight: 600; color: #334155;">{seg_name}</td>
                            <td class="num-col">{format_currency(seg_data['vab_rj_mi'])}</td>
                            <td class="num-col" style="color: {color}; {bold}">{lq:.2f}</td>
                            <td class="num-col">{m_prod:.2f}x</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
                <p style="font-size: 0.5em; color: #94a3b8; text-align: left; margin-top: 15px;">* LQ > 1 indica que o estado tem concentração produtiva no setor superior à média nacional.</p>
            </section>
"""

    # Add slides for each event
    events = [k for k in data.keys() if k != 'estudo_central']
    for idx, event_name in enumerate(events):
        ev = data[event_name]
        
        # Event Title Slide
        html += f"""
            <section>
                <h2 style="font-size: 1.8em;" class="gradient-text">Simulação: {event_name}</h2>
                <p style="color: #64748b;">{ev['descricao']}</p>
            </section>
"""
        
        # Event KPIs Slide
        html += f"""
            <section>
                <h3 style="font-size: 1.3em;">Métricas Globais do Evento</h3>
                <div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; margin-top: 40px;">
                    <div style="width: 45%; background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: left;">
                        <p style="font-size: 0.6em; color: #64748b; font-weight: bold; text-transform: uppercase; margin: 0 0 5px 0;">Choque Direto (Demanda)</p>
                        <p style="font-size: 1.6em; font-weight: 800; color: #0f172a; margin: 0;">{format_currency(ev['choque_total'])} Mi</p>
                    </div>
                    <div style="width: 45%; background: #eff6ff; padding: 20px; border-radius: 12px; border: 1px solid #bfdbfe; text-align: left;">
                        <p style="font-size: 0.6em; color: #2563eb; font-weight: bold; text-transform: uppercase; margin: 0 0 5px 0;">Produção Induzida (BR)</p>
                        <p style="font-size: 1.6em; font-weight: 800; color: #1e3a8a; margin: 0;">{format_currency(ev['producao_total_brasil'])} Mi</p>
                        <p style="font-size: 0.5em; color: #3b82f6; margin: 5px 0 0 0;">Multiplicador: {ev['multiplicador_brasil']:.3f}x</p>
                    </div>
                    <div style="width: 45%; background: #f0fdf4; padding: 20px; border-radius: 12px; border: 1px solid #bbf7d0; text-align: left;">
                        <p style="font-size: 0.6em; color: #16a34a; font-weight: bold; text-transform: uppercase; margin: 0 0 5px 0;">Empregos Gerados</p>
                        <p style="font-size: 1.6em; font-weight: 800; color: #14532d; margin: 0;">{format_number(ev['empregos_total_brasil'])}</p>
                    </div>
                    <div style="width: 45%; background: #fffbeb; padding: 20px; border-radius: 12px; border: 1px solid #fde68a; text-align: left;">
                        <p style="font-size: 0.6em; color: #d97706; font-weight: bold; text-transform: uppercase; margin: 0 0 5px 0;">Retorno Fiscal (ICMS+ISS)</p>
                        <p style="font-size: 1.6em; font-weight: 800; color: #78350f; margin: 0;">{format_currency(ev['fiscal_rj'])} Mi</p>
                        <p style="font-size: 0.5em; color: #b45309; margin: 5px 0 0 0;">{ev['fiscal_rj']/ev['choque_total']*100:.1f}% do choque inicial</p>
                    </div>
                </div>
            </section>
"""

        # Event Assumptions (Choque) Slide
        html += f"""
            <section>
                <h3 style="font-size: 1.2em;">Premissas do Choque</h3>
                <p style="font-size: 0.6em; color: #64748b;">Como a demanda final foi distribuída na Matriz Insumo-Produto</p>
                
                <table class="creative-table" style="font-size: 0.55em; margin-top: 10px;">
                    <thead>
                        <tr>
                            <th>Setor (IBGE)</th>
                            <th class="num-col">Choque Direto (R$ Mi)</th>
                            <th class="num-col">% Total</th>
                            <th style="text-align: center;">Tipo</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        shock_sectors = [s for s in ev['setores_detalhados_rj'] if s.get('choque_direto', 0) > 0]
        shock_sectors.sort(key=lambda x: x['choque_direto'], reverse=True)
        for i, s in enumerate(shock_sectors[:8]): # limit to top 8 to fit on slide
            badge_color = "#3b82f6" if s['criativo'] else "#94a3b8"
            type_text = "Criativo" if s['criativo'] else "Não-Criativo"
            pct = s['choque_direto'] / ev['choque_total'] * 100
            html += f"""
                        <tr>
                            <td style="width: 50%;">{s['setor']}</td>
                            <td class="num-col" style="font-weight: bold;">{format_currency(s['choque_direto'])}</td>
                            <td class="num-col">{pct:.1f}%</td>
                            <td style="text-align: center;"><span style="background: {badge_color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">{type_text}</span></td>
                        </tr>
"""
        if len(shock_sectors) > 8:
            html += """<tr><td colspan="4" style="text-align: center; font-style: italic;">... (outros setores omitidos)</td></tr>"""
            
        html += """
                    </tbody>
                </table>
            </section>
"""

        # Event Creative Segments
        html += f"""
            <section>
                <h3 style="font-size: 1.2em;">Apropriação por Segmento Criativo</h3>
                
                <table class="creative-table" style="font-size: 0.6em;">
                    <thead>
                        <tr>
                            <th>Segmento</th>
                            <th class="num-col">Produção Induzida (R$ Mi)</th>
                            <th class="num-col">Empregos Totais</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        seg_data = ev['segmentos_criativos']
        for k, v in sorted(seg_data.items(), key=lambda item: item[1]['producao'], reverse=True):
            html += f"""
                        <tr>
                            <td style="font-weight: bold; color: #334155;">{k}</td>
                            <td class="num-col" style="color: #2563eb; font-weight: bold;">{format_currency(v['producao'])}</td>
                            <td class="num-col">{format_number(v['empregos'])}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </section>
"""

        # Event Spillover Chart
        states_only = [s for s in ev['spillover_por_estado'] if s['uf'] != 'RJ'][:6]
        states_labels = [s['uf'] for s in states_only]
        states_prods = [s['producao'] for s in states_only]
        
        html += f"""
            <section>
                <h3 style="font-size: 1.2em;">Vazamento Inter-estadual (Spillover)</h3>
                <p style="font-size: 0.6em; color: #64748b;">R$ {format_currency(ev['producao_outros_estados'])} Mi ({ev['producao_outros_estados']/ev['producao_total_brasil']*100:.1f}%) transbordam para outros estados via importação intermédias.</p>
                <div class="chart-container">
                    <canvas id="chartSpillover_{idx}"></canvas>
                </div>
            </section>

            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    // wait for chart.js loading
                    setTimeout(() => {{
                        const ctx = document.getElementById('chartSpillover_{idx}').getContext('2d');
                        new Chart(ctx, {{
                            type: 'bar',
                            data: {{
                                labels: {json.dumps(states_labels)},
                                datasets: [{{
                                    label: 'Produção (R$ Mi)',
                                    data: {json.dumps(states_prods)},
                                    backgroundColor: '#8b5cf6',
                                    borderRadius: 4
                                }}]
                            }},
                            options: {{
                                responsive: true,
                                maintainAspectRatio: false,
                                plugins: {{ legend: {{ display: false }} }},
                                scales: {{ y: {{ beginAtZero: true }} }}
                            }}
                        }});
                    }}, 500);
                }});
            </script>
"""

        # Top Indirect Needs
        html += f"""
            <section>
                <h3 style="font-size: 1.1em;">Efeito Indireto: Setores Não-Criativos</h3>
                <p style="font-size: 0.55em; color: #64748b; margin-bottom: 20px;">Indústrias de base e serviços utilitários tracionados primariamente pela cadeia criativa.</p>
                <table class="creative-table" style="font-size: 0.5em;">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>Setor MIP</th>
                            <th class="num-col">Produção (R$ Mi)</th>
                            <th class="num-col">Empregos</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        top_nc = ev['setores_nao_criativos_rj'][:7]
        for i, s in enumerate(top_nc):
            html += f"""
                        <tr>
                            <td style="color: #94a3b8;">{i+1}</td>
                            <td>{s['setor']}</td>
                            <td class="num-col" style="color: #059669; font-weight: bold;">{format_currency(s['producao'])}</td>
                            <td class="num-col">{format_number(s['empregos'])}</td>
                        </tr>
"""
        html += """
                    </tbody>
                </table>
            </section>
"""

    html += """
            <!-- Slide Final -->
            <section>
                <h2 style="font-size: 1.8em;" class="gradient-text">Obrigado</h2>
                <p style="color: #64748b; margin-top: 1em;">Estudo elaborado com MRIO v4 (2021)</p>
                <p style="font-size: 0.6em; color: #94a3b8; margin-top: 2em;">Pressione ESC para visão geral da apresentação.</p>
            </section>

        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/reveal.js/4.5.0/reveal.min.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: 'c/t',
            transition: 'slide',
            backgroundTransition: 'fade',
            width: 1024,
            height: 768,
            margin: 0.04,
            minScale: 0.2,
            maxScale: 2.0
        });
    </script>
</body>
</html>
"""
    out_path = OUTPUT_DIR / 'apresentacao_economia_criativa.html'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Apresentação HTML salva em: {out_path}")

if __name__ == "__main__":
    with open(OUTPUT_DIR / 'relatorio_economia_criativa_completo.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    generate_presentation(data)
