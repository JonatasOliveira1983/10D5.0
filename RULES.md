# RULES.md — 10D Sniper V4.2 "Unified Pipeline Elite"
# Invariantes Tecnicas Inegociaveis — [PERSISTÊNCIA ABSOLUTA]
# Leia INTEIRO antes de tocar em qualquer arquivo.
# Fonte da verdade: codigo real no Railway e PostgreSQL/WebSocket Nativo.

---

## 🛡️ PROTOCOLO DE BLINDAGEM V4.0 (CRÍTICO)
1. **AUTO-CURA DE BANCO:** O sistema realiza migrações automáticas de esquema no boot. Qualquer divergência de coluna deve ser corrigida via script integrado ao `database_service.py`.
2. **TIMEZONE INTEGRITY (CRÍTICO):** É obrigatório o uso de `datetime.utcnow().replace(tzinfo=None)` ou `datetime.utcnow()` para todas as interações e comparações com o Postgres. **NUNCA** use `datetime.now(timezone.utc)` para comparações diretas com timestamps do banco, pois isso gera erro de "offset-naive vs offset-aware". SSOT: Naive UTC.
3. **ARQUIVAMENTO ATÔMICO:** É terminantemente proibido limpar um slot sem antes garantir o arquivamento no Postgres via `database_service.log_trade`.
4. **PAPER MODE ENFORCEMENT:** Em modo de teste, a variável `BYBIT_EXECUTION_MODE` deve ser injetada como `PAPER` no Railway para garantir o saldo simulado de $100.
5. **META DE LUCRO 10/10 (V4.0):** O contador de progresso diário (Dashboard) e o contador de ciclos do Vault (1/10) só incrementam se o lucro líquido da ordem (PNL) for **>= $10.00**.

---

## ⚡ 10D BYBITY REAL 4.0 — PROTOCOLO DE ELITE
## REGRA 00 — REPOSITÓRIO ÚNICO E OFICIAL
1. **REPO ÚNICO:** O único repositório oficial para este sistema é: `https://github.com/JonatasOliveira1983/10D5.0/`.
2. **PUSH OBRIGATÓRIO:** Todo commit deve ser enviado para o branch `main` deste repositório para deploy automático no Railway.
3. **URL DE COMANDO:** A UI oficial é acessível via `https://1crypten.space/`.

---

## REGRA 0 — PROTOCOLO DE INFRAESTRUTURA RAILWAY (SOVEREIGN)
1. **SSOT (Source of Truth):** O banco de dados primário é o **PostgreSQL (Railway)**. O `SovereignService` é o único orquestrador autorizado de persistência.
2. **BROADCAST:** Toda comunicação com a UI é feita via **WebSocket Nativo (/ws/cockpit)**.
3. **VAULT HISTORY:** O histórico de trades deve ser recuperado via `database_service` e exposto pela API `/api/history`. Retornar listas vazias na UI por falha de serviço soberano é inaceitável.
4. **EMANCIPAÇÃO TOTAL:** O uso de Firebase/Firestore/RTDB foi **EXTINTO**. O sistema opera de forma 100% autônoma.

---

## 1. SISTEMA DE SLOTS — ATRIBUICAO FIXA
| Slot | Tipo       | Estrategia   | Moonbag?                     | Leverage      |
|------|------------|--------------|------------------------------|---------------|
| 1    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 2    | BLITZ_30M  | BlitzSniper  | Condicional (pos 300% ROI)   | 50x fixo      |
| 3    | SWING      | Harvester    | SIM (emancipa em 150% ROI)   | 50x fixo      |
| 4    | SWING      | Harvester    | SIM (emancipa em 150% ROI)   | 50x fixo      |

- **REGRA:** Alavancagem de 50x é OBRIGATÓRIA para todos os slots para maximizar o potencial da banca Sniper.
- **REGRA:** Slots 1 e 2 são EXCLUSIVOS para BlitzSniper. Nunca atribua outro tipo.
- **REGRA:** Collision Guard impede o mesmo ativo em mais de um slot simultaneamente via `paper_positions` e Postgres.

---

## 2. GENESIS ID — PASSAPORTE DA ORDEM
- **Geração Instantânea:** O `genesis_id` é gerado no momento do nascimento da ordem, inclusive em Paper Mode.
- **Formato Atômico:** `BLZ-{UUID6}-{SYM4}` (Blitz) / `SWG-{UUID6}-{SYM4}` (Swing)
- **REGRA:** O `genesis_id` é persistido no **PostgreSQL** e transmitido via **WebSocket** imediatamente.
- **REGRA:** genesis_id deve acompanhar a ordem até o fechamento.

---

## 3. BLITZ SNIPER & DNA SPECIALIST (V4.0 ADAPTIVE)
1. **Matriz de Especialista (40 Pares):** O Bibliotecário possui um DNA fixo para 40 ativos selecionados (sem Memecoins, sem BTC/ETH/SOL). Cada ativo tem seu buffer de respiro e atraso de RF configurados.
2. **Paciência do Sniper (Violinada):** O `AmbushAgent` não executa sinais no toque cego. Ele aguarda uma "absorção" (pavio/wick) no gráfico de 1m para garantir a rejeição de preço antes do "Strike".
3. **Adaptive Respiro (V4.0):** Tolerância de desvio de ROI específica por ativo (de 8% a 25%) se o fluxo (CVD) estiver a favor.
4. **Breakeven Inteligente (ADX-Aware):** Gatilho de Risk-Free ajustado pela força da tendência. ADX > 40 = Trava em 20% ROI. ADX < 22 = Trava em 40% ROI.
5. **Paciência Diplomática (V4.0):** O Sentinela concede até 90 segundos de carência se o fluxo monetário (CVD) sustentar a posição.

---

## 4. RADAR DE INTELIGÊNCIA — BROADCAST LOCAL
- **Sincronização:** Os sinais são enviados via WebSocket para a UI em tempo real (`type: radar_pulse`).
- **ESTRUTURA DE DADOS:** O pacote de radar_pulse DEVE ser um objeto completo `{signals, decisions, market_context}`. O frontend rejeita arrays puros para evitar quebra de HUD.

---

## 5. ORÁCULO DE MERCADO — ESTABILIZAÇÃO ÁGIL
- **Boot Time:** Reduzido para **15-30 segundos** no Railway.
- **Fallback ADX:** Se o Oráculo estiver estabilizando, o sistema usa o ADX bruto do WebSocket para não travar o Radar.

---

## 6. GESTÃO DE RISCO — BANKROLL RAILWAY
- **Banca Padrão:** **$100.00** (Simulado/Paper).
- **Margem por slot:** **10% da banca** ($10.00 por ordem).
- **Meta Diária:** Exige lucro de $10.00 por trade para contar no placar 10/10.

---

## 7. HIERARQUIA DE AGENTES (SOBERANIA RAILWAY)
```
Captain (Orquestrador Central)
  ├── BlitzSniper   -> Monitor M30 (Slots 1-2)
  ├── Harvester     -> Monitor H1/H4 (Slots 3-4 - SWING)
  ├── Oracle        -> Inteligencia de Mercado (ADX/BTC Pulse)
  ├── Librarian     -> DNA Specialist (Mola/Trap/Respiro)
  └── WebSocket     -> Broadcast de Estado para o Cockpit UI
```

---

## 8. DESIGN INVARIANTE — SEAMLESS PREMIUM
1. **Estética:** Grayscale Premium (Preto, Branco, Cinza e Verde Normal `#22c55e`). **PROIBIDO LIMA.**
2. **Glassmorphism:** Uso obrigatório de `backdrop-blur-xl` em todos os painéis.
3. **Labels de Histórico:** Devem seguir o padrão `+R$ 0,00` com vírgula para decimais.

---

## 9. MAPA DE ESTADO SOBERANO
| Componente | Localização Primária (SSOT) |
|---|---|
| **Slots Ativos** | Tabela `slots` (Postgres) |
| **Moonbags** | Tabela `moonbags` (Postgres) |
| **Histórico Vault** | Tabela `trade_history` (Postgres) |
| **Motor Paper** | Tabela `system_state` (Postgres) |

---

## 10. PROTOCOLO DE EXPURGO DE FANTASMAS & GENESIS GUARD (V4.0)
- **Auto-Purge:** Ativos em erro de subscrição são filtrados na carga do estado Paper.
- **Lixo Visual:** Registros com PNL $0 ou ID de recuperação são expurgados do histórico visual (`RECOVERY-%`).
- **Genesis Guard:** Ordens sem DNA de inteligência (emergência) recebem telemetria padrão para evitar erro de "Relatório Inexistente" na UI.

---

## 11. INTEGRIDADE DE ASSINATURA WEBSOCKET (BYBIT-WS)
1. **Blocklist Guard:** Ativos na `settings.ASSET_BLOCKLIST` são ignorados no WS (exceto BTC).
2. **Type Safety:** Handlers validam se a mensagem é um dicionário antes do processamento.

---

## 12. INTELIGÊNCIA COLETIVA E AGENTE VISÃO (V4.2.1 — CASCATA & GATE)
1. **Vision Gate Inteligente:** O Agente Visão só captura screenshots e aciona a IA se: (a) houver slots livres (< 4), (b) o Bibliotecário não tiver vetado o ativo, e (c) o score inicial for >= 70. Isso economiza quota de API e foca no que importa.
2. **Cascata de IA Gratuita:** O sistema utiliza uma cascata de modelos multimodal (vision) gratuitos via OpenRouter (Gemini 2.0 Flash Free, Llama 4 Scout, etc.).
   - Se um modelo atinge rate-limit (429), o sistema tenta o próximo da lista.
   - Se um modelo exige pagamento (402), ele é removido da lista permanentemente até o próximo reboot.
3. **Veto Obrigatório Universal:** O **Agente Visão** e o **Bibliotecário** continuam sendo filtros OBRIGATÓRIOS. Se todos os modelos da cascata falharem, a ordem é bloqueada por segurança (`[VISION-OFFLINE-BLOCK]`).
4. **Fluxo Otimizado:**
   ```
   Sinal → Bibliotecário (DNA) → [VISION GATE] → Visão (Cascata Free) → Capitão → Ordem
   ```
5. **UI AI Cascade Monitor:** O Cockpit exibe em tempo real (Painel Lateral) qual modelo está sendo usado, o volume de requisições e o estado de saúde (Active/Cooling/Dead) de cada modelo na cascata.
6. **UI Sovereign Intelligence:** Todas as convocações do Capitão, scans do Bibliotecário e vetos do Visão são transmitidos via WebSocket em tempo real para o Cockpit.

---

## 13. OBSERVATORY (VISUAL HQ) & SERVICE WORKER
1. **Observatory (V5.8):** O sistema possui um hub visual dedicado (`/observatory`) embutindo gráficos nativos do TradingView via `widgetembed` iframe. É a zona estéril onde as SMAs (21/100) e o Volume são expostos em tempo real para a frota e para o operador humano.

### 📜 Estabilidade Técnica (V4.2.1)
- **Schema Parity**: Todo campo adicionado ao dicionário de atualização do Slot deve obrigatoriamente existir no modelo `Slot` do `database_service.py` e ser incluído no `migrate_db.py`.
- **Atomic Initialization**: Flags de inteligência (`is_spring_strike`, `is_shadow_strike`, etc) devem ser pré-declaradas no início do método `open_position` com fallbacks seguros (`.get(key, default)`) para prevenir `NameError`.
- **Sanitized Persist**: O método `update_slot` deve filtrar chaves do dicionário para garantir que apenas atributos válidos do modelo sejam passados ao construtor SQLAlchemy.
- **Matrix Consistency**: 40 Ativos especialistas (SPECIALIST_MATRIX) exclusivamente no M30 para sinais.
- **Broadcast Protocol**: WebSocket Soberano para broadcast em tempo real para a UI.
- **Persistence Layer**: Persistência obrigatória em Postgres (Railway) com modelo SQLAlchemy sincronizado.
2. **Rota Isolada:** A rota `/observatory` não deve cair no catch-all de SPA do FastAPI. Ela retorna o arquivo `observatory.html` fisicamente.
3. **Service Worker (PWA):** O arquivo `sw.js` **obrigatoriamente** utiliza estratégia `Network-First` para a rota `/observatory` e `/cockpit.html`. O fallback do Service Worker jamais deve devolver o Cockpit em chamadas para o Observatory, devendo o cache versionado (`CACHE_NAME`) ser elevado em caso de conflitos de roteamento.

---

## 14. ARQUITETURA UNIFICADA DE SLOTS — PIPELINE V4.2 (LEI MÁXIMA)

### 14.1 Roteamento de Slots — Regra Inegociável
| Slot | Tipo       | Origem do Sinal | Biblioteca de Ativos        |
|------|------------|-----------------|-----------------------------|
| 1    | BLITZ_30M  | BlitzSniper M30 | 40 Pares SPECIALIST_MATRIX  |
| 2    | BLITZ_30M  | BlitzSniper M30 | 40 Pares SPECIALIST_MATRIX  |
| 3    | SWING      | SignalGenerator | 40 Pares SPECIALIST_MATRIX  |
| 4    | SWING      | SignalGenerator | 40 Pares SPECIALIST_MATRIX  |

### 14.2 Regras de Negócio do Pipeline Unificado
1. **SPECIALIST_MATRIX é a única fonte de ativos.** Tanto o BlitzSniper (`scan_and_inject`) quanto o SignalGenerator (`monitor_and_generate`) operam **exclusivamente** sobre os 40 pares definidos em `LibrarianAgent.SPECIALIST_MATRIX`. Ativos fora da matriz não geram ordens.
2. **BTC é referência, não alvo.** O `BTCUSDT.P` é monitorado pelo Radar para contexto (ADX, variação, direção) mas **nunca** é alvo de ordem nos slots.
3. **O Capitão é o único autorizador.** Todo sinal (BLITZ ou SWING) deve passar pelo `CaptainAgent._process_single_signal` antes de virar ordem. Injeções diretas na exchange sem passar pelo Capitão são proibidas.
4. **Slot-Type explícito obrigatório.** O campo `slot_type` deve ser determinado explicitamente antes da chamada a `bankroll_manager.can_open_new_slot()`:
   - `is_blitz=True` / `layer=BLITZ` / `timeframe=30` → `slot_type = "BLITZ_30M"`
   - Demais sinais → `slot_type = "SWING"`
5. **MATRIX-VETO no Capitão:** Se o ativo não estiver na `SPECIALIST_MATRIX`, o `_get_fleet_consensus` retorna veto imediato (`approved: False`) sem consultar o Visão.

### 14.3 Identificadores de Sinal para Diagnóstico nos Logs
- `⚡ [BLITZ-MATRIX]` → BlitzSniper usando SPECIALIST_MATRIX corretamente
- `⚡ [BLITZ-MATRIX-FALLBACK]` → BlitzSniper em fallback (Bibliotecário ainda inicializando)
- `⚓ [V4.2 SLOT-ROUTING] ... → Slot Type: BLITZ_30M` → Capitão roteando para Slots 1&2
- `⚓ [V4.2 SLOT-ROUTING] ... → Slot Type: SWING` → Capitão roteando para Slots 3&4
- `🚫 [MATRIX-VETO]` → Ativo rejeitado por não estar na SPECIALIST_MATRIX

---

*Versão: V4.2.1 "Vision Cascade & Gate" | Atualizado: 2026-04-27*
*Este arquivo é a ÚNICA FONTE DA VERDADE. Repositório Oficial: 10D5.0.*
