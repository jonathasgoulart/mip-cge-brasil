import React, { useState, useEffect } from 'react';
import {
  Activity, TrendingUp, Users, DollarSign, Plus, Trash2, RefreshCcw, Zap, Globe, Layers, Database, ShieldCheck, Download, Map, LayoutPanelLeft, Info, X
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts';

const PRIMARY_COLOR = '#6366f1';

// Use environment variable for production, fallback to local
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const AGG_GROUPS = {
  macro: [
    { name: "Agropecu\u00e1ria", range: [0, 3] },
    { name: "Ind\u00fastria", range: [3, 37] },
    { name: "Servi\u00e7os", range: [37, 67] }
  ],
  intermediate: [
    { name: "Agropecu\u00e1ria e Extra\u00e7\u00e3o", range: [0, 3] },
    { name: "Extra\u00e7\u00e3o e Minera\u00e7\u00e3o", range: [3, 7] },
    { name: "Ind\u00fastria de Alimentos e Refino", range: [7, 20] },
    { name: "Outras Ind\u00fastrias", range: [20, 37] },
    { name: "Utilidades P\u00fablicas", range: [37, 39] },
    { name: "Constru\u00e7\u00e3o Civil", range: [39, 40] },
    { name: "Com\u00e9rcio", range: [40, 41] },
    { name: "Transportes e Log\u00edstica", range: [41, 45] },
    { name: "Alojamento e Alimenta\u00e7\u00e3o", range: [45, 47] },
    { name: "Servi\u00e7os Profissionais e TI", range: [47, 64] },
    { name: "Cultura, Lazer e Pessoais", range: [64, 67] }
  ]
};

const App = () => {
  const [regions, setRegions] = useState([]);
  const [sectors, setSectors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const [selectedRegion, setSelectedRegion] = useState('RJ');
  const [activeShocks, setActiveShocks] = useState([]);
  const [aggLevel, setAggLevel] = useState('detailed');
  const [requireSpillover, setRequireSpillover] = useState(false);
  const [outputAgg, setOutputAgg] = useState('detailed');
  const [isMethodologyOpen, setIsMethodologyOpen] = useState(false);

  useEffect(() => {
    const fetchSectors = async () => {
      try {
        const res = await fetch(`${API_URL}/metadata/sectors?level=${aggLevel.toLowerCase()}`);
        setSectors(await res.json());
        setActiveShocks([]);
        setResults(null);
      } catch (err) { }
    };
    fetchSectors();
  }, [aggLevel]);

  useEffect(() => {
    const fetchRegions = async () => {
      try {
        const res = await fetch(`${API_URL}/metadata/regions`);
        setRegions(await res.json());
      } catch (err) { }
    };
    fetchRegions();
  }, []);

  const handleRunSimulation = async () => {
    if (activeShocks.length === 0) return;
    setLoading(true);
    const shocksMap = {};
    activeShocks.forEach(s => { shocksMap[s.sectorId] = parseFloat(s.value); });

    try {
      const resp = await fetch(`${API_URL}/simulate/demand`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          region: selectedRegion,
          shocks: shocksMap,
          aggregation_level: aggLevel,
          require_spillover: requireSpillover
        })
      });
      const data = await resp.json();
      if (data && data.results) setResults(data);
    } catch (err) { alert("Erro na simula\u00e7\u00e3o."); }
    setLoading(false);
  };

  const handleExportExcel = async () => {
    if (!results) return;
    try {
      const resp = await fetch(`${API_URL}/export/excel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(results)
      });
      const blob = await resp.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `IMPACTO_${selectedRegion}_${new Date().toISOString().split('T')[0]}.xlsx`;
      document.body.appendChild(a); a.click(); a.remove();
    } catch (err) { alert("Erro ao exportar Excel."); }
  };

  const getDisplayResults = () => {
    if (!results) return [];
    if (outputAgg === 'detailed') return results.results;

    const groups = AGG_GROUPS[outputAgg];
    return groups.map(g => {
      const sub = results.results.filter(r => r.id >= g.range[0] && r.id < g.range[1]);
      return {
        name: g.name,
        production: sub.reduce((acc, curr) => acc + curr.production, 0),
        jobs: sub.reduce((acc, curr) => acc + curr.jobs, 0)
      };
    }).sort((a, b) => b.production - a.production);
  };

  const displayResults = getDisplayResults();
  const taxData = results?.fiscal_detail ? Object.entries(results.fiscal_detail)
    .filter(([_, v]) => v > 0).sort((a, b) => b[1] - a[1]) : [];

  return (
    <div className="min-h-screen pb-20 overflow-x-hidden bg-[#020617] text-slate-200 text-sm">
      <header className="sticky top-0 z-50 px-6 py-4">
        <div className="max-w-7xl mx-auto glass px-6 py-3 flex items-center justify-between border-white/5 bg-slate-900/40 rounded-3xl border backdrop-blur-xl">
          <div className="flex items-center gap-3">
            <Activity className="text-indigo-500 w-6 h-6" />
            <div>
              <h1 className="text-xl font-bold text-white tracking-tight">MIP-CGE</h1>
              <p className="text-[10px] text-slate-400 font-bold uppercase leading-none mt-1">Simulador Brasil v7.0</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <button onClick={() => setIsMethodologyOpen(true)} className="flex items-center gap-2 px-3 py-1.5 bg-slate-800/50 hover:bg-slate-700/50 border border-white/10 rounded-full text-[10px] font-black text-slate-300 transition-all">
              <Info size={14} className="text-indigo-400" /> METODOLOGIA
            </button>
            {results && (
              <button onClick={handleExportExcel} className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-[10px] font-black text-emerald-400 hover:bg-emerald-500 hover:text-white transition-all">
                <Download size={14} /> DOWNLOAD EXCEL
              </button>
            )}
            <div className="hidden sm:block px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full text-[9px] font-black text-indigo-400 uppercase tracking-widest">
              MRIO v7.0 (NEREUS) Active
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* Controls Panel */}
          <div className="lg:col-span-4 space-y-6">
            <div className="glass p-7 space-y-8 bg-slate-900/60 rounded-3xl border border-white/10 shadow-2xl">
              <div className="flex items-center justify-between border-b border-white/5 pb-4">
                <h2 className="text-lg font-black text-white flex items-center gap-3"><Zap className="text-amber-400 fill-amber-400/20" /> PARÂMETROS</h2>
                <div className="flex items-center gap-2">
                  <span className="text-[9px] font-black text-slate-500">MRIO SPILLOVER</span>
                  <button onClick={() => setRequireSpillover(!requireSpillover)} className={`w-10 h-5 rounded-full relative transition-all ${requireSpillover ? 'bg-indigo-600' : 'bg-slate-800'}`}>
                    <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${requireSpillover ? 'left-6' : 'left-1'}`} />
                  </button>
                </div>
              </div>

              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-black text-slate-400 flex items-center gap-2"><Globe size={14} className="text-indigo-400" /> Região do Choque</label>
                  <select className="w-full h-12 px-4 rounded-xl bg-slate-950 border border-white/10 text-white font-bold focus:border-indigo-500 focus:outline-none transition-all" value={selectedRegion} onChange={(e) => setSelectedRegion(e.target.value)}>
                    {regions.map(r => <option key={r} value={r} className="bg-slate-900">{r}</option>)}
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-black text-slate-400 flex items-center gap-2"><Layers size={14} className="text-purple-400" /> Agregação do Input</label>
                  <div className="grid grid-cols-3 gap-2 bg-slate-950/40 p-1 rounded-xl border border-white/5">
                    {['detailed', 'intermediate', 'macro'].map(l => (
                      <button key={l} onClick={() => setAggLevel(l)} className={`text-[9px] py-2.5 rounded-lg font-black transition-all ${aggLevel === l ? 'bg-indigo-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>
                        {l.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-2">
                  <label className="text-[10px] uppercase font-black text-slate-400 flex items-center gap-2"><LayoutPanelLeft size={14} className="text-emerald-400" /> Agregação do Resultado</label>
                  <div className="grid grid-cols-3 gap-2 bg-slate-950/40 p-1 rounded-xl border border-white/5">
                    {['detailed', 'intermediate', 'macro'].map(l => (
                      <button key={l} onClick={() => setOutputAgg(l)} className={`text-[9px] py-2.5 rounded-lg font-black transition-all ${outputAgg === l ? 'bg-emerald-600 text-white shadow-lg' : 'text-slate-500 hover:text-slate-300'}`}>
                        {l.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="space-y-3 pt-2">
                  <label className="text-[10px] uppercase font-black text-slate-400 flex items-center gap-2"><Database size={14} className="text-indigo-400" /> Definição do Choque</label>
                  <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                    {activeShocks.map((s, idx) => (
                      <div key={idx} className="p-5 rounded-2xl bg-slate-950/60 border border-white/5 relative group hover:border-indigo-500/30 transition-all">
                        <Trash2 onClick={() => setActiveShocks(activeShocks.filter((_, i) => i !== idx))} size={16} className="absolute -top-2 -right-2 text-rose-500 cursor-pointer bg-slate-900 rounded-full p-0.5 opacity-0 group-hover:opacity-100 transition-all hover:scale-110" />
                        <select className="w-full bg-transparent text-[11px] font-black text-white border-b border-white/10 pb-2 focus:outline-none" value={s.sectorId} onChange={(e) => {
                          const newS = [...activeShocks]; newS[idx].sectorId = e.target.value; setActiveShocks(newS);
                        }}>
                          {sectors.map(sec => <option key={sec.id} value={sec.id} className="bg-slate-900">{sec.name}</option>)}
                        </select>
                        <div className="mt-2 relative">
                          <input type="number" value={s.value} className="w-full bg-slate-950 border border-white/5 rounded-xl pl-8 py-2 text-sm font-black text-white focus:outline-none" onChange={(e) => {
                            const newS = [...activeShocks]; newS[idx].value = e.target.value; setActiveShocks(newS);
                          }} />
                          <span className="absolute left-3 top-2 text-indigo-500 text-[9px] font-black">R$</span>
                          <span className="absolute right-4 top-2 text-[10px] font-black text-slate-600 uppercase">Mi</span>
                        </div>
                      </div>
                    ))}
                    <button className="w-full py-4 border-2 border-dashed border-white/10 rounded-2xl text-slate-500 hover:text-indigo-400 hover:border-indigo-500/40 transition-all text-[11px] font-black uppercase tracking-widest flex items-center justify-center gap-2"
                      onClick={() => setActiveShocks([...activeShocks, { sectorId: sectors[0]?.id, value: 100 }])}>
                      <Plus size={14} strokeWidth={3} /> Adicionar Item
                    </button>
                  </div>
                </div>
              </div>

              <button className="w-full py-5 bg-indigo-600 hover:bg-indigo-500 rounded-2xl shadow-xl text-xs font-black uppercase transition-all disabled:opacity-50 text-white flex items-center justify-center gap-4"
                onClick={handleRunSimulation} disabled={loading || activeShocks.length === 0}>
                {loading ? <RefreshCcw className="animate-spin w-5 h-5" /> : <TrendingUp size={22} />}
                <span>{loading ? 'PROCESSANDO...' : 'RODAR SIMULAÇÃO'}</span>
              </button>
            </div>
          </div>

          <div className="lg:col-span-8 space-y-6">
            {!results ? (
              <div className="glass h-[700px] flex flex-col items-center justify-center text-center p-12 bg-slate-950/20 rounded-[3rem] border border-white/5">
                <Activity size={48} className="text-slate-700 animate-pulse mb-8" />
                <h3 className="text-2xl font-black text-white tracking-tight">Pronto para Simular</h3>
                <p className="text-slate-500 mt-4 max-w-sm text-sm font-medium">Configure o choque setorial e a regi\u00e3o e clique em Rodar Simula\u00e7\u00e3o.</p>
              </div>
            ) : (
              <div className="space-y-6 animate-in fade-in duration-700">
                {/* KPIs */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  {[
                    { label: 'Produ\u00e7\u00e3o Total', val: `R$ ${(results.summary?.total_production || 0).toLocaleString()}M`, icon: <DollarSign />, cl: 'text-indigo-400 bg-indigo-500/10' },
                    { label: 'Novos Empregos', val: Math.round(results.summary?.total_jobs || 0).toLocaleString(), icon: <Users />, cl: 'text-emerald-400 bg-emerald-500/10' },
                    { label: 'Arrecada\u00e7\u00e3o', val: `R$ ${(results.summary?.total_tax || 0).toFixed(1)}M`, icon: <ShieldCheck />, cl: 'text-amber-400 bg-amber-500/10' },
                    { label: 'Spillover', val: `R$ ${(results.summary?.spillover_production || 0).toFixed(1)}M`, icon: <Map />, cl: 'text-purple-400 bg-purple-500/10' },
                  ].map((k, i) => (
                    <div key={i} className="glass p-5 rounded-3xl border border-white/10 bg-slate-900/40">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-[9px] font-black uppercase text-slate-500">{k.label}</span>
                        <div className={`p-1.5 rounded-lg border border-white/5 ${k.cl}`}>{k.icon}</div>
                      </div>
                      <div className="text-xl font-black text-white">{k.val}</div>
                    </div>
                  ))}
                </div>

                {/* Fiscal Detailed Breakdown */}
                <div className="glass p-8 rounded-3xl border border-white/10 bg-slate-900/40">
                  <h3 className="text-lg font-black text-white flex items-center gap-3 mb-8 uppercase tracking-tight"><ShieldCheck className="text-amber-500 w-5 h-5" /> Arrecadação Detalhada</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {taxData.map((t, i) => (
                      <div key={i} className="p-4 rounded-2xl bg-slate-950/40 border border-white/5 space-y-2">
                        <span className="text-[9px] font-black text-slate-500 uppercase">{t[0]}</span>
                        <div className="text-lg font-black text-white tabular-nums">R$ {t[1].toFixed(2)}M</div>
                        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
                          <div className="h-full bg-amber-500" style={{ width: `${Math.min(100, (t[1] / (results.summary.total_tax || 1)) * 100)}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="glass p-8 rounded-3xl border border-white/10 bg-slate-900/40">
                    <h3 className="text-sm font-black text-slate-400 mb-6 uppercase tracking-widest">Impacto em Produção (Top 10)</h3>
                    <div className="h-[250px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={displayResults.slice(0, 10)}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                          <XAxis dataKey="name" stroke="#475569" tick={{ fontSize: 9 }} interval={0} angle={-35} textAnchor="end" height={60} />
                          <Tooltip contentStyle={{ background: '#020617', border: 'none', borderRadius: '15px', color: '#fff' }} />
                          <Bar dataKey="production" fill={PRIMARY_COLOR} radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div className="glass p-8 rounded-3xl border border-white/10 bg-slate-900/40">
                    <h3 className="text-sm font-black text-slate-400 mb-6 uppercase tracking-widest">Geração de Empregos (Top 10)</h3>
                    <div className="h-[250px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={displayResults.slice(0, 10)}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                          <XAxis dataKey="name" stroke="#475569" tick={{ fontSize: 9 }} interval={0} angle={-35} textAnchor="end" height={60} />
                          <Tooltip contentStyle={{ background: '#020617', border: 'none', borderRadius: '15px' }} />
                          <Bar dataKey="jobs" fill="#10b981" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                </div>

                {/* State Spillover Results Table */}
                {results.spillover && results.spillover.length > 0 && (
                  <div className="glass p-8 rounded-3xl border border-white/10 bg-slate-900/40">
                    <div className="flex items-center justify-between mb-8">
                      <h3 className="text-lg font-black text-white flex items-center gap-3 uppercase tracking-tight"><Map className="text-purple-400 w-5 h-5" /> Transbordamento Interestadual</h3>
                      <span className="text-[10px] font-black text-slate-500 uppercase tracking-widest">{results.spillover.length} Estados Impactados</span>
                    </div>
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      <div className="h-[280px]">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={results.spillover.slice(0, 12)}>
                            <XAxis dataKey="state" stroke="#475569" tick={{ fontSize: 10, fontWeight: 'bold' }} />
                            <Bar dataKey="production" fill="#a855f7" radius={[4, 4, 0, 0]} />
                            <Tooltip contentStyle={{ background: '#020617', border: 'none' }} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                      <div className="overflow-x-auto max-h-[280px] custom-scrollbar rounded-2xl border border-white/5 bg-slate-950/20">
                        <table className="w-full text-xs text-left">
                          <thead className="sticky top-0 bg-slate-900 z-10 text-slate-500 font-bold uppercase tracking-widest text-[8px] border-b border-white/5">
                            <tr><th className="p-4">Estado (UF)</th><th className="p-4 text-right">Prod. (Mi)</th><th className="p-4 text-right">Ocupa\u00e7\u00f5es</th></tr>
                          </thead>
                          <tbody className="divide-y divide-white/5">
                            {results.spillover.map((s, idx) => (
                              <tr key={idx} className="hover:bg-white/5 transition-all">
                                <td className="p-4 font-black text-slate-300">{s.state}</td>
                                <td className="p-4 text-right font-black text-white tabular-nums">R$ {s.production.toFixed(2)}</td>
                                <td className="p-4 text-right font-black text-purple-400 tabular-nums">{Math.round(s.jobs).toLocaleString()}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                )}

                {/* Detailed Main Results Table */}
                <div className="glass overflow-hidden rounded-3xl border border-white/10 bg-slate-900/40">
                  <div className="px-8 py-5 border-b border-white/5 bg-white/[0.02] flex items-center justify-between">
                    <h3 className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">Detalhamento Setorial Completo ({outputAgg.toUpperCase()})</h3>
                    <div className="text-[9px] font-black text-indigo-400 uppercase tracking-widest">Ordenado por Produ\u00e7\u00e3o</div>
                  </div>
                  <div className="overflow-x-auto max-h-[500px] custom-scrollbar">
                    <table className="w-full text-left text-xs">
                      <thead className="sticky top-0 bg-slate-950 z-20 text-slate-500 font-bold uppercase tracking-widest text-[9px] border-b border-white/5">
                        <tr><th className="px-8 py-5">Atividade / Categoria</th><th className="px-8 py-5 text-right">Produ\u00e7\u00e3o Impactada (Mi)</th><th className="px-8 py-5 text-right">Postos de Trabalho</th></tr>
                      </thead>
                      <tbody className="divide-y divide-white/5 font-display">
                        {displayResults.map((r, i) => (
                          <tr key={i} className="hover:bg-white/[0.03] transition-all">
                            <td className="px-8 py-5 font-black text-slate-200 uppercase tracking-tight">{r.name}</td>
                            <td className="px-8 py-5 text-right font-black text-white tabular-nums">R$ {r.production.toLocaleString()}M</td>
                            <td className="px-8 py-5 text-right font-black text-emerald-400 tabular-nums">{Math.round(r.jobs).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      <footer className="max-w-7xl mx-auto px-6 mt-20 pb-12 text-center opacity-30 select-none">
        <div className="flex flex-col items-center gap-2">
          <p className="text-[9px] font-black tracking-[0.5em] uppercase text-white">MODELO MRIO-BRASIL 7.0 | IIOAS 2019</p>
          <p className="text-[8px] font-black text-slate-500 uppercase tracking-widest">Tecnologia Inter-regional NEREUS/USP | Tributos IBGE 2019</p>
        </div>
      </footer>

      {/* Methodology Modal */}
      {isMethodologyOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-300">
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" onClick={() => setIsMethodologyOpen(false)} />
          <div className="relative w-full max-w-5xl max-h-[90vh] overflow-y-auto custom-scrollbar glass bg-slate-900/95 border border-white/10 rounded-3xl shadow-2xl p-8 sm:p-10">
            <button onClick={() => setIsMethodologyOpen(false)} className="absolute top-6 right-6 p-2 rounded-full bg-white/5 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-all">
              <X size={20} className="stroke-[3]" />
            </button>

            <div className="flex items-center gap-4 mb-8">
              <div className="p-3 bg-indigo-500/20 rounded-2xl border border-indigo-500/30 text-indigo-400">
                <Info size={28} />
              </div>
              <div>
                <h2 className="text-2xl font-black text-white tracking-tight">Metodologia do Simulador Escala Brasil</h2>
                <p className="text-xs font-bold uppercase tracking-widest text-slate-500 mt-1">Como a Matrix MRIO v7.0 calcula os impactos</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-white/10 pb-3">
                  <Globe className="text-blue-400" size={20} />
                  <h3 className="text-sm font-black text-white uppercase tracking-widest">1. Motor Leontief (NEREUS)</h3>
                </div>
                <p className="text-slate-400 text-xs leading-relaxed font-medium">
                  Utilizamos a <strong>Matriz de Insumo-Produto Inter-Regional Oficial (MRIO v7.0)</strong>, cobrindo 67 setores e as 27 Unidades Federativas. Diferente de modelos teóricos (antigo modelo gravitacional de Haversine), nossa matriz engloba <strong className="text-indigo-300">fluxos interestaduais documentados e reais</strong> extraídos da colossal base IIOAS-BRUF (NEREUS/USP, 2025). O simulador capta exatamente os vazamentos monetários fidedignos—diagnosticando matematicamente o quanto Goiás compra de insumos de São Paulo num choque simulado.
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-white/10 pb-3">
                  <Users className="text-emerald-400" size={20} />
                  <h3 className="text-sm font-black text-white uppercase tracking-widest">2. Emprego e Renda (PNAD)</h3>
                </div>
                <p className="text-slate-400 text-xs leading-relaxed font-medium">
                  Atrelado ao volume de produção, o impacto social de trabalho é derivado dos microdados da <strong>PNAD Contínua 2021 (IBGE)</strong>. Convertimos horas trabalhadas isoladas e salários estaduais em <strong className="text-emerald-300">Coeficientes de Produtividade Regionais Diferenciados</strong>. Isto dita que investir R$ 1 Milhão em agricultura na Bahia gera uma estatística intrinsecamente diferente (historicamente provada) de vagas de trabalho do que os mesmos R$ 1 Mi na agricultura mecânica do Rio Grande do Sul.
                </p>
              </div>

              <div className="space-y-4">
                <div className="flex items-center gap-3 border-b border-white/10 pb-3">
                  <ShieldCheck className="text-amber-400" size={20} />
                  <h3 className="text-sm font-black text-white uppercase tracking-widest">3. Tributação Estadual Híbrida</h3>
                </div>
                <p className="text-slate-400 text-xs leading-relaxed font-medium">
                  Os coeficientes fiscais ($\tau$) substituem brutas aproximações por uma <strong>Matriz de "Sharing Factors"</strong> fundamentada em arrecadações reportadas pelo CONFAZ e auditadas via Sistema de Contas Nacionais IBGE. Isso garante que impostos como o <strong className="text-amber-300">ICMS</strong> não sejam taxados medianamente pelo país; cada estado aplica sua intensidade tributária estatística observada em cima do Valor Bruto de sua respectiva Produção Setorial, gerando alta fidedignidade em arrecadação na ponta final de governos locais.
                </p>
              </div>
            </div>

            <div className="mt-10 p-5 bg-indigo-500/10 border border-indigo-500/20 rounded-2xl flex items-start gap-4">
              <Zap className="text-indigo-400 mt-1 shrink-0" size={20} fill="currentColor" />
              <div>
                <h4 className="text-sm font-black text-white mb-1 uppercase tracking-widest">O Efeito Spillover Transbordante</h4>
                <p className="text-slate-300 text-xs leading-relaxed font-medium">
                  Ao ativar a flag de Spillover (MRIO Spillover), o algoritmo matricial Leontief não apenas aplica as fórmulas no estado inicial sede, porém, através das interconexões vetoriais cruzadas de Comércio Interestadual que possuímos mapeados, <strong className="text-white">projeta a onde a riqueza transbordará para o resto da Nação</strong>. Você mapeará na tabela verde/roxa qual foi o estado que mais proveu serviços/insumos para a realização do evento base no primeiro estado.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
