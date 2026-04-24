import re
import os

files = [
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\index.html",
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\cockpit.html"
]

backtest_component = """
        // [NEW] Backtest Lab - Piloto de Testes (V110.29.0)
        const BacktestLab = () => {
            const [eligible, setEligible] = React.useState([]);
            const [selectedCoin, setSelectedCoin] = React.useState('ALL');
            const [status, setStatus] = React.useState({ eligible_pairs: 0, total_klines: 0, details: [] });
            
            // Toggles
            const [toggles, setToggles] = React.useState({
                lateral_guillotine: true,
                sentinel: false
            });

            React.useEffect(() => {
                fetch('http://localhost:8085/api/backtest/eligible')
                    .then(r => r.json())
                    .then(data => {
                        setEligible(data);
                        if(data.length > 0) setSelectedCoin('ALL');
                    })
                    .catch(e => console.error(e));
                    
                fetchStatus();
            }, []);

            const fetchStatus = () => {
                fetch('http://localhost:8085/api/backtest/status')
                    .then(r => r.json())
                    .then(data => setStatus(data))
                    .catch(console.error);
            };

            const downloadData = () => {
                const payload = selectedCoin === 'ALL' ? {} : { symbols: [selectedCoin] };
                fetch('http://localhost:8085/api/backtest/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                }).then(r => r.json()).then(d => {
                    alert('Download iniciado no servidor background proxy!');
                });
            };

            const runSimulation = () => {
                alert('A arquitetura do Mock Broker Simulator será executada aqui no backend!');
            };

            const handleToggle = (key) => setToggles(p => ({ ...p, [key]: !p[key] }));

            return (
                <div className="min-h-screen p-8 animate-in fade-in slide-in-from-bottom-4 relative z-10 w-full overflow-hidden flex flex-col pt-12 lg:pt-8 bg-black/90">
                    <div className="flex items-center justify-between mb-8 pb-4 border-b border-primary/20">
                        <div className="flex items-center gap-4">
                            <h1 className="text-2xl font-display font-black text-white tracking-widest uppercase flex items-center gap-2">
                                <span className="material-icons-round text-primary text-3xl">science</span>
                                Piloto de Testes Sniper
                            </h1>
                            <span className="px-3 py-1 bg-primary/20 text-primary text-[10px] font-bold rounded-full border border-primary/40 uppercase tracking-widest">Lab V1.0</span>
                        </div>
                    </div>

                    <div className="flex flex-col lg:flex-row gap-6 flex-1 min-h-0">
                        {/* Painel Lateral - Controles */}
                        <div className="w-full lg:w-80 flex flex-col gap-6 shrink-0 overflow-y-auto no-scrollbar">
                            <div className="glass-card p-6 rounded-3xl border border-white/5 space-y-4">
                                <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Dados Históricos</h2>
                                
                                <div className="space-y-2">
                                    <label className="text-[10px] text-slate-500 font-bold uppercase">Moeda Alvo</label>
                                    <select 
                                        className="w-full bg-slate-900 border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:border-primary outline-none"
                                        value={selectedCoin} onChange={e => setSelectedCoin(e.target.value)}
                                    >
                                        <option value="ALL">💰 TODAS ELEGÍVEIS</option>
                                        {eligible.map(e => <option key={e.symbol} value={e.symbol}>{e.symbol} (Max {e.max_leverage}x)</option>)}
                                    </select>
                                </div>
                                <button onClick={downloadData} className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/20 rounded-xl transition-all text-white">
                                    <span className="material-icons-round text-sm">cloud_download</span>
                                    <span className="text-xs font-bold uppercase tracking-wider">Baixar Passado (Bybit)</span>
                                </button>
                                
                                <div className="mt-4 p-4 bg-primary/5 border border-primary/10 rounded-xl">
                                    <p className="text-[10px] text-slate-400 font-medium tracking-wide">STATUS BANCO LOCAL:</p>
                                    <div className="flex justify-between items-center mt-2 text-white">
                                        <span className="text-xs font-bold">Klines Coletadas:</span>
                                        <span className="text-primary font-black bg-primary/10 px-2 py-1 rounded">{status.total_klines.toLocaleString()}</span>
                                    </div>
                                    <button onClick={fetchStatus} className="text-[10px] text-primary underline mt-4 w-full text-center hover:text-white">Atualizar Status Database</button>
                                </div>
                            </div>

                            <div className="glass-card p-6 rounded-3xl border border-white/5 space-y-4">
                                <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Mutações Engine</h2>
                                
                                {[
                                    { id: 'lateral_guillotine', label: 'Guilhotina Lateral (ADX < 28)' },
                                    { id: 'sentinel', label: 'Protocolo Sentinel (False Wicks)' }
                                ].map(t => (
                                    <div key={t.id} className="flex items-center justify-between p-4 bg-black/40 rounded-xl border border-white/5">
                                        <span className="text-[10px] font-bold text-white uppercase tracking-wider">{t.label}</span>
                                        <button onClick={() => handleToggle(t.id)} className={`relative w-12 h-6 rounded-full transition-colors shrink-0 ${toggles[t.id] ? 'bg-primary' : 'bg-slate-700'}`}>
                                            <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-black transition-transform ${toggles[t.id] ? 'translate-x-6' : 'translate-x-0'}`}></div>
                                        </button>
                                    </div>
                                ))}
                            </div>
                            
                            <button onClick={runSimulation} className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-primary text-black border border-primary/40 rounded-2xl hover:bg-primary/80 transition-all font-black uppercase tracking-widest relative overflow-hidden group shadow-[0_0_20px_rgba(255,215,0,0.2)]">
                                <span className="material-icons-round text-lg group-hover:rotate-180 transition-transform duration-500">sync</span>
                                INJETAR BACKTEST
                            </button>
                        </div>

                        {/* Painel Principal - Tela Wide de Resultados */}
                        <div className="flex-1 glass-card border border-white/5 rounded-3xl p-6 flex flex-col min-w-0 bg-slate-900/30">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest">Ranking de Eficiência Hídrica (Top 50)</h2>
                                <span className="text-[10px] text-slate-500 uppercase tracking-widest border border-slate-700 px-2 py-1 rounded">Resultado Simulado</span>
                            </div>
                            
                            <div className="flex-1 overflow-x-auto overflow-y-auto no-scrollbar">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="border-b border-white/10 text-[10px] font-black text-slate-500 uppercase tracking-widest bg-black/20">
                                            <th className="p-4 rounded-tl-xl">Rank</th>
                                            <th className="p-4">Par Tático</th>
                                            <th className="p-4">Win Rate</th>
                                            <th className="p-4 text-center">Trades</th>
                                            <th className="p-4 text-right">PnL Líquido</th>
                                            <th className="p-4 text-right rounded-tr-xl">Max Drawdown</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {[1,2,3].map(i => (
                                            <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                                                <td className="p-4 text-slate-500 font-black">#{i}</td>
                                                <td className="p-4 font-black tracking-widest text-white">---</td>
                                                <td className="p-4 text-slate-600 font-bold">0%</td>
                                                <td className="p-4 text-slate-600 text-center">-</td>
                                                <td className="p-4 text-right font-display text-lg text-slate-600">$0.00</td>
                                                <td className="p-4 text-slate-600 text-xs text-right">0%</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                <div className="mt-20 text-center text-slate-500 flex flex-col items-center">
                                    <span className="material-icons-round text-5xl mb-4 opacity-20">hourglass_empty</span>
                                    <p className="text-xs font-bold uppercase tracking-widest opacity-50">Motores Desligados. Baixe os Dados para começar.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            );
        };
"""

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. DELETE CPRO STUDY PAGE SPECIFICALLY
    # We delete from `// [NEW] CPRO Study System` to just before `const NavBar = `
    cpro_pattern = re.compile(r'\s*\/\/\s*\[NEW\] CPRO Study System - 2026 Transition.+?(?=\s*const NavBar\s*=)', re.DOTALL)
    if 'CPRO Study System' in content:
        content = cpro_pattern.sub('\n\n        ', content)

    # 2. DELETE OLD ROUTE & CPRO Sub-Link navigation
    content = re.sub(r'<Route\s+path="/estudo-cpro".+?/>', '', content)
    
    # We look for the exact CPRO nav button we might have had. It was already removed but just in case:
    cpro_btn_pattern = re.compile(r'<Link to="/estudo-cpro" className="flex items-center gap-2 p-3 bg-indigo-500/10.+?<\/Link>', re.DOTALL)
    content = cpro_btn_pattern.sub('', content)

    # 3. INJECT BACKTEST LAB COMPONENT
    if "const BacktestLab =" not in content:
        content = content.replace("const SettingsPage =", backtest_component + "\n        const SettingsPage =")

    # 4. INJECT ROUTE
    if '<Route path="/backtest"' not in content:
        content = re.sub(r'(<Route\s+path="/config"\s+element=\{<SettingsPage[^>]+>\}\s*/>)',
                         r'\1\n                                <Route path="/backtest" element={<BacktestLab />} />', content)

    # 5. INJECT BUTTON IN CONFIG
    nav_button = """
                                <h3 className="text-[9px] font-black uppercase text-slate-500 tracking-[0.2em] mb-4">SISTEMA DE BACKTEST</h3>
                                <Link to="/backtest" className="flex justify-between items-center p-4 bg-primary/10 border border-primary/20 rounded-2xl hover:bg-primary/20 transition-all font-black text-primary uppercase tracking-widest text-[10px] group mb-8">
                                    <div className="flex items-center gap-3">
                                        <span className="material-icons-round text-primary group-hover:scale-110 transition-transform">science</span>
                                        Laboratório de Piloto de Testes (Engine Local)
                                    </div>
                                    <span className="material-icons-round text-primary opacity-50 group-hover:opacity-100 group-hover:translate-x-1 transition-all">chevron_right</span>
                                </Link>
"""
    if "SISTEMA DE BACKTEST" not in content:
        content = content.replace('<h3 className="text-[9px] font-black uppercase text-slate-500 tracking-[0.2em] mb-4">SISTEMA CORE</h3>', nav_button + '\n                                <h3 className="text-[9px] font-black uppercase text-slate-500 tracking-[0.2em] mb-4">SISTEMA CORE</h3>')

    # Quick check to ensure NavBar is still there!
    if 'const NavBar =' not in content:
        print(f"ERROR: NavBar somehow got wiped in {filepath}!")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Injected fixes successfully!")
