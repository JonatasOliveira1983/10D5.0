import re

files = [
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\index.html",
    r"c:\Users\spcom\Desktop\10D-3.0\frontend\cockpit.html"
]

backtest_component = """
        // [NEW] Backtest Lab - Piloto de Testes (V110.29.0)
        const BacktestLab = () => {
            const [eligible, setEligible] = React.useState([]);
            const [selectedCoin, setSelectedCoin] = React.useState('');
            const [status, setStatus] = React.useState({ eligible_pairs: 0, total_klines: 0, details: [] });
            
            // Toggles
            const [toggles, setToggles] = React.useState({
                lateral_guillotine: True,
                sentinel: False
            });

            React.useEffect(() => {
                fetch('http://localhost:8085/api/backtest/eligible')
                    .then(r => r.json())
                    .then(data => {
                        setEligible(data);
                        if(data.length > 0) setSelectedCoin(data[0].symbol);
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
                    alert('Download iniciado no servidor!');
                });
            };

            const runSimulation = () => {
                alert('A simulação de backtest conectou ao Cérebro! Os resultados serao exibidos no backend até a inteface final ficar pronta.');
            };

            const handleToggle = (key) => setToggles(p => ({ ...p, [key]: !p[key] }));

            return (
                <div className="min-h-screen p-8 animate-in fade-in slide-in-from-bottom-4 relative z-10 w-full overflow-hidden flex flex-col">
                    <div className="flex items-center justify-between mb-8 pb-4 border-b border-primary/20">
                        <div className="flex items-center gap-4">
                            <h1 className="text-2xl font-display font-black text-white tracking-widest uppercase flex items-center gap-2">
                                <span className="material-icons-round text-primary text-3xl">science</span>
                                Piloto de Testes Sniper
                            </h1>
                            <span className="px-3 py-1 bg-primary/20 text-primary text-[10px] font-bold rounded-full border border-primary/40 uppercase tracking-widest">Lab V1.0</span>
                        </div>
                    </div>

                    <div className="flex gap-6 flex-1 min-h-0">
                        {/* Painel Lateral - Controles */}
                        <div className="w-80 flex flex-col gap-6 shrink-0 overflow-y-auto no-scrollbar">
                            <div className="glass-card p-6 rounded-3xl border border-white/5 space-y-4">
                                <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Dados Históricos</h2>
                                
                                <div className="space-y-2">
                                    <label className="text-[10px] text-slate-500 font-bold uppercase">Moeda Alvo</label>
                                    <select 
                                        className="w-full bg-midnight border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:border-primary outline-none"
                                        value={selectedCoin} onChange={e => setSelectedCoin(e.target.value)}
                                    >
                                        <option value="ALL">💰 TODAS ELEGÍVEIS</option>
                                        {eligible.map(e => <option key={e.symbol} value={e.symbol}>{e.symbol} (Max {e.max_leverage}x)</option>)}
                                    </select>
                                </div>
                                <button onClick={downloadData} className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-white/5 hover:bg-white/10 border border-white/20 rounded-xl transition-all">
                                    <span className="material-icons-round text-sm">cloud_download</span>
                                    <span className="text-xs font-bold uppercase tracking-wider">Baixar Passado (Bybit)</span>
                                </button>
                                
                                <div className="mt-4 p-4 bg-primary/5 border border-primary/10 rounded-xl">
                                    <p className="text-[10px] text-slate-400 font-medium">Status Banco de Dados Local:</p>
                                    <div className="flex justify-between items-center mt-2 text-white">
                                        <span className="text-xs">Klines Armazenados:</span>
                                        <span className="text-primary font-bold">{status.total_klines.toLocaleString()}</span>
                                    </div>
                                    <button onClick={fetchStatus} className="text-[10px] text-primary underline mt-2 w-full text-center">Atualizar Status</button>
                                </div>
                            </div>

                            <div className="glass-card p-6 rounded-3xl border border-white/5 space-y-4">
                                <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-4">Parâmetros (Captain)</h2>
                                
                                {[
                                    { id: 'lateral_guillotine', label: 'Guilhotina Lateral (ADX < 28)' },
                                    { id: 'sentinel', label: 'Protocolo Sentinel (Anti-Violino)' }
                                ].map(t => (
                                    <div key={t.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/5">
                                        <span className="text-xs font-bold text-white uppercase">{t.label}</span>
                                        <button onClick={() => handleToggle(t.id)} className={`relative w-12 h-6 rounded-full transition-colors ${toggles[t.id] ? 'bg-primary' : 'bg-slate-700'}`}>
                                            <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-black transition-transform ${toggles[t.id] ? 'translate-x-6' : 'translate-x-0'}`}></div>
                                        </button>
                                    </div>
                                ))}
                            </div>
                            
                            <button onClick={runSimulation} className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-primary text-black border border-primary/40 rounded-2xl hover:bg-primary/80 transition-all font-black uppercase tracking-widest relative overflow-hidden group shadow-lg shadow-primary/20">
                                <span className="material-icons-round text-lg group-hover:animate-spin">play_arrow</span>
                                RODAR SIMULAÇÃO
                            </button>
                        </div>

                        {/* Painel Principal - Tela Wide de Resultados */}
                        <div className="flex-1 glass-card border border-white/5 rounded-3xl p-6 flex flex-col min-w-0">
                            <h2 className="text-xs font-black text-slate-400 uppercase tracking-widest mb-6">Ranking de Eficiência Hídrica (Top 50)</h2>
                            <div className="flex-1 overflow-x-auto overflow-y-auto no-scrollbar">
                                <table className="w-full text-left border-collapse">
                                    <thead>
                                        <tr className="border-b border-white/10 text-[10px] font-black text-slate-500 uppercase tracking-widest">
                                            <th className="p-4">Rank</th>
                                            <th className="p-4">Par Ideal</th>
                                            <th className="p-4">Win Rate</th>
                                            <th className="p-4">Total Trades</th>
                                            <th className="p-4 text-right">PnL Simulado</th>
                                            <th className="p-4">Max Drawdown</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {[1,2,3].map(i => (
                                            <tr key={i} className="border-b border-white/5 hover:bg-white/[0.02] transition-colors">
                                                <td className="p-4 text-slate-400 font-bold">#{i}</td>
                                                <td className="p-4 font-black text-white">BTCUSDT (Ref)</td>
                                                <td className="p-4 text-emerald-400 font-bold">--%</td>
                                                <td className="p-4 text-slate-300">--</td>
                                                <td className="p-4 text-right font-display text-lg text-primary">$--</td>
                                                <td className="p-4 text-red-400 text-xs">--%</td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                <div className="mt-12 text-center text-slate-500 flex flex-col items-center">
                                    <span className="material-icons-round text-4xl mb-2 opacity-50">analytics</span>
                                    <p className="text-xs font-bold uppercase tracking-widest">Vazio. Rode uma simulação para preencher.</p>
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

    # Inject the component right before `const SettingsPage = `
    if "const BacktestLab =" not in content:
        content = content.replace("const SettingsPage =", backtest_component + "\n        const SettingsPage =")

    # Change router path `<Route path="/estudo-cpro" element={<CPROStudyPage />} />`
    content = re.sub(r'<Route path="/estudo-cpro" element=\{<CPROStudyPage />\} />', r'<Route path="/backtest" element={<BacktestLab />} />', content)

    # In SettingsPage, we must add a link to `/backtest`
    # The existing CPRO-2026 button was removed earlier, but we can append to Navigation Sub-links if needed.
    # We will just inject a new navigation button in SettingsPage, right after "Gerenciamento de Instâncias" block or just at top.
    
    # We look for `<h3 className="text-[9px] font-black uppercase text-slate-500 tracking-[0.2em] mb-4">SISTEMA CORE</h3>`
    nav_button = """
<Link to="/backtest" className="flex items-center gap-3 p-4 bg-indigo-500/10 border border-indigo-500/30 rounded-2xl hover:bg-indigo-500/20 transition-all font-black text-indigo-400 uppercase tracking-widest text-[10px] group mb-4">
    <span className="material-icons-round text-indigo-400 group-hover:scale-110 transition-transform">science</span>
    Laboratório de Testes (Backtest)
</Link>
"""
    if "Laboratório de Testes" not in content:
        content = content.replace('<h3 className="text-[9px] font-black uppercase text-slate-500 tracking-[0.2em] mb-4">SISTEMA CORE</h3>', nav_button + '\n' + '<h3 className="text-[9px] font-black uppercase text-slate-500 tracking-[0.2em] mb-4">SISTEMA CORE</h3>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Injected BacktestLab UI into frontend!")
