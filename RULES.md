# RULES.md — 10D Sniper V110.209 "Smart PWA Architecture"
# Invariantes Tecnicas Inegociaveis — [PERSISTÊNCIA ABSOLUTA]
# Leia INTEIRO antes de tocar em qualquer arquivo.
# Fonte da verdade: codigo real no Railway e PostgreSQL/WebSocket Nativo.

---

## 🛡️ PROTOCOLO DE BLINDAGEM V110.209 (CRÍTICO)
1. **AUTO-CURA DE BANCO:** O sistema deve realizar migrações automáticas de esquema no boot. Qualquer divergência de coluna deve ser corrigida via script `migrate_db.py` integrado ao `main.py`.
2. **CAIXA PRETA DE EMERGÊNCIA:** Se o registro de um trade no banco de dados falhar, o sistema DEVE salvar o payload completo em `emergency_trades.json`. Perder dados de lucro por erro de DB é uma violação gravíssima.
3. **ARQUIVAMENTO ATÔMICO:** É terminantemente proibido limpar um slot sem antes garantir o arquivamento (seja no DB ou na Caixa Preta).
4. **PWA & SMART CACHE:** O Service Worker deve operar em modo Network-First para o HTML e Stale-While-Revalidate para CDNs. Desativar o SW via scripts de "nuke" é proibido, exceto em caso de corrupção total de dados.

---

## ⚡ 10D BYBITY REAL 4.0 — PROTOCOLO DE ELITE — V110.209
## REGRA 00 — REPOSITÓRIO ÚNICO E OFICIAL
1. **REPO ÚNICO:** O único repositório oficial para este sistema é: `https://github.com/JonatasOliveira1983/10D5.0/`.
2. **DEPRECATED:** O repositório `10DBybityREAL` foi desativado e não deve mais ser utilizado para push ou sincronização.

## REGRA 0 — PROTOCOLO DE INFRAESTRUTURA RAILWAY (SOVEREIGN)
1. **SSOT (Source of Truth):** O banco de dados primário é o **PostgreSQL (Railway)**, gerenciado pelo `database_service.py`.
2. **BROADCAST:** Toda comunicação com a UI é feita via **WebSocket Nativo (/ws/cockpit)**. O motor `Sovereign-WS` no frontend substitui permanentemente o Firebase RTDB.
3. **UNIVERSAL BRIDGE:** O `cockpit.html` possui um script embutido que atua como ponte universal, traduzindo pacotes WebSocket em atualizações de estado para os hooks React. Qualquer alteração no `app.jsx` deve ser sincronizada com o bloco script do `cockpit.html`.
4. **EMANCIPAÇÃO TOTAL:** O uso de Firebase/Firestore/RTDB foi **EXTINTO**. O sistema opera via `SovereignService` e `websocket_service`, garantindo autonomia total.

---

## 1. SISTEMA DE SLOTS — ATRIBUICAO FIXA (V110.137)

| Slot | Tipo       | Estrategia   | Moonbag?                     | Leverage      |
|------|------------|--------------|------------------------------|---------------|
| 1    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 2    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 3    | SWING      | Wyckoff      | SIM (emancipa em 150% ROI)   | Quartermaster |
| 4    | SWING      | Wyckoff      | SIM (emancipa em 150% ROI)   | Quartermaster |

**Arquivo:** `bankroll.py::get_slot_type()`
**REGRA:** Slots 1 e 2 sao EXCLUSIVOS para BlitzSniper. Nunca atribua outro tipo.
**REGRA:** Sinais SWING nunca vao para Slots 1-2. Blitz nunca vai para Slots 3-4.
**REGRA:** Collision Guard impede o mesmo ativo em mais de um slot simultaneamente via `paper_positions` e Postgres.

---

## 2. GENESIS ID — PASSAPORTE DA ORDEM (V110.175 SOVEREIGN)

**Arquivo:** `bankroll.py::open_position()`, `bybit_rest.py::place_atomic_order()`

- **Geracao Instantanea:** O `genesis_id` e gerado no momento do nascimento da ordem, inclusive em Paper Mode.
- **Formato Atomico:** `BLZ-{UUID6}-{SYM4}` (Blitz) / `SWG-{UUID6}-{SYM4}` (Swing)
- **REGRA:** O `genesis_id` e persistido no **PostgreSQL** e transmitido via **WebSocket** imediatamente.
- **REGRA:** genesis_id deve acompanhar a ordem ate o fechamento (inclusive no Moonbag se houver).
- **REGRA [V110.175]:** Se as chaves Bybit estiverem ausentes, o sistema entra em **AUTO-PAPER MODE** e usa o ID local.

---

## 3. BLITZ SNIPER — DOUTRINA DAS 10 (V110.175)

**Doutrina Blitz Sniper (Slots 1 e 2 — v110.175)**
*Status: OPERATIONAL | Mode: RAILWAY STRIKE*

1. **Momento Mola**: Prioridade absoluta para sinais "Mola" identificados pelo Librarian.
2. **Spring Shield (Bypass)**: Sinais de Mola possuem bypass total da Guilhotina Lateral (ADX < 18) e do Trap-Prone Shield.
3. **Strike Entry**: Sinais com Score >= 70 executam entrada imediata no modo Blitz.
4. **Paper Freedom**: No modo PAPER, o Capitão ignora bloqueios de "Bull Trap" e "Baixa Confiança" para permitir a validação da execução.

---

## 4. RADAR DE INTELIGÊNCIA — BROADCAST LOCAL (V110.175)

**Arquivo:** `signal_generator.py`, `websocket_service.py`

- **Sincronizacao:** Os sinais sao enviados via WebSocket para a UI em tempo real (`type: radar_pulse`).
- **ESTRUTURA DE DADOS [V110.192]:** O pacote de radar_pulse DEVE ser um objeto completo `{signals, decisions, market_context}`. O frontend rejeita arrays puros para evitar quebra de HUD.
- **Filtro de Swing:** Sinais de Swing (Harvester) sao exibidos nos Slots 3-4 e no Radar com badge AMBAR.
- **Filtro de Blitz:** Sinais de Blitz (BlitzSniper) sao exibidos nos Slots 1-2 e no Radar com badge BRANCA.

---

## 5. ORÁCULO DE MERCADO — ESTABILIZAÇÃO ÁGIL (V110.175)

**Arquivo:** `oracle_agent.py`

- **Boot Time:** Reduzido para **15-30 segundos** no Railway.
- **Fallback ADX:** Se o Oráculo estiver estabilizando, o sistema usa o ADX bruto do WebSocket para não travar o Radar.
- **Intelligence:** ADX, Preço e Dominância são transmitidos via `SYSTEM_STATE` no WebSocket nativo.

---

## 6. GESTAO DE RISCO — BANKROLL RAILWAY

**Arquivo:** `bankroll.py`, `database_service.py`

- **Banca Padrao:** **$100.00** (Simulado/Paper).
- **Margem por slot:** **10% da banca** ($10.00 por ordem).
- **Persistencia:** O saldo e o historico sao salvos no **PostgreSQL**. O reset de banca limpa o banco de dados local do Railway.

---

## 7. HIERARQUIA DE AGENTES (SOBERANIA RAILWAY)

```
Captain (Orquestrador Central)
  ├── BlitzSniper   -> Monitor M30 (Slots 1-2)
  ├── Harvester     -> Monitor H1/H4 (Slots 3-4 - SWING)
  ├── Oracle        -> Inteligencia de Mercado (ADX/BTC Pulse)
  ├── Librarian     -> DNA do Ativo (Mola/Trap/Wick)
  └── WebSocket     -> Broadcast de Estado para o Cockpit UI
```

**REGRA:** Nenhum agente deve depender do Firebase para funcionar.
**REGRA:** O sistema deve ser auto-suficiente dentro do container Railway.

---

## 8. DESIGN INVARIANTE — SEAMLESS PREMIUM (V110.175)
- **Estética:** Grayscale Premium (Preto, Branco, Cinza e Lima).
- **Glassmorphism:** Uso obrigatório de `backdrop-blur-xl` em todos os painéis.
- **Badge Contrast:** `BLITZ_30M` (Branco) | `SWING` (Ambar).

---

*Versão: V110.209 "Smart PWA Architecture" | Atualizado: 2026-04-25*
*Este arquivo é a ÚNICA FONTE DA VERDADE. O sistema foi TOTALMENTE EMANCIPADO do Firebase via WebSocket nativo e Postgres.*
