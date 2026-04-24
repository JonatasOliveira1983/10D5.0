# RULES.md — 10D Sniper V110.173 "Elite Spring Doctrine"
# Invariantes Tecnicas Inegociaveis
# Leia INTEIRO antes de tocar em qualquer arquivo.
# Fonte da verdade: codigo real (nao documentacao narrativa).

---

## ⚡ 10D BYBITY REAL 4.0 — PROTOCOLO DE ELITE — V110.173
## REGRA 0 — PROTOCOLO DE LEITURA OBRIGATORIO
Antes de qualquer edicao em arquivos de servico, execute:
1. Ler este arquivo (RULES.md)
2. Consultar MASTER_ARCHITECTURE.md para contexto da versao
3. Rodar grep no arquivo alvo para verificar dependencias reais

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
**REGRA:** Collision Guard impede o mesmo ativo em mais de um slot simultaneamente.

---

## 2. GENESIS ID — PASSAPORTE DA ORDEM (V110.172 IRON LOCK)

**Arquivo:** `bankroll.py::open_position()`, `firebase_service.py::register_order_genesis()`

- Gerado em: TODA abertura de ordem (Blitz e Swing)
- **[V110.172] Formato Atomico:** `BLZ-{BYBIT_ORDER_ID}-{SYM4}` (Blitz) / `SWG-{BYBIT_ORDER_ID}-{SYM4}` (Swing)
  - O `genesis_id` e gerado SOMENTE APOS a Exchange confirmar a ordem (`orderId` Bybit).
  - Se o `orderId` nao estiver disponivel (Paper Mode), usa `LOCAL_{UUID6}` como fallback.
  - Colisoes entre ordens sao matematicamente impossiveis com este esquema.
- Colecao Firestore: `orders_genesis` (documento imutavel)
- Campos obrigatorios: genesis_id, strategy, strategy_label, symbol, entry_price, sl_price, tp_price,
  leverage, slot_id, signal_score, opened_at, events[], units_extracted, status
- **REGRA:** genesis_id deve acompanhar a ordem ate o fechamento (inclusive no Moonbag se houver)
- **REGRA [V110.160]:** Deve ser visivel e legivel de forma proeminente no Cockpit UI.
- **REGRA [V110.172 GLOBAL LOCK]:** `CaptainAgent._process_single_signal` DEVE verificar `bankroll_manager.pending_slots` antes de iniciar o processamento. Se o simbolo ja esta em transicao, abortar com `[GLOBAL IN-MEMORY LOCK]`.
- **REGRA [V110.172 PAPER DESYNC GUARD]:** `can_open_new_slot` e `get_specific_empty_slot` DEVEM consultar `bybit_rest_service.paper_positions` para validar slots ANTES de aceitar o estado do Firestore. Firebase pode estar desatualizado; a memoria local nao.


---

## 3. BLITZ SNIPER — DOUTRINA DAS 10 (V110.144)

**Doutrina Blitz Sniper (Slots 1 e 2 — v110.170)**

O modo Blitz evolui para a **Doutrina de Ataque Elite (Strike & Pullback Elite)**.
*Status: OPERATIONAL | Mode: FLEET STRIKE*

## 🚀 V110.170: Blitz Recovery & Momento Mola
- **Protocolo Momento Mola**: Prioridade absoluta para sinais "Mola" identificados pelo Librarian.
- **Whale Trap Reversal**: Inversão automática de lado (Long <-> Short) se detectado risco de liquidação institucional (Whale Trap).
- **Direct/Strike Entry**: Bypass automático do AmbushAgent (Tocaia) para sinais Blitz quando **BTC ADX > 25**.
- **M30 Fibonacci**: Uso de TF 30M para cálculos de retração em sinais de tiro curto (Blitz).
- **Radar Sync**: Publicação forçada de sinais `spring_elite_list` (Top 40) no RTDB para visibilidade total no Cockpit.
 [V110.151] Possui **Micro-Tocaia** com tolerância de 0.1% para evitar perda de bote.
    *   **Modo STRIKE (ROMPIMENTO)**: Ativado por consenso absoluto (**Whale Pulse + SMA Cross + Nectar Seal**). O Captão ignora a espera técnica e executa entrada imediata com confirmação de fluxo de 5s.
    *   **SPRING STRIKE (MOMENTO MOLA)**:
        - [V110.160] **REACTIVE SPRING**: Detecção de Mola movida para o Sniper (M30 Real-time) para ignorar o atraso de 2h do Librarian.
        - [V110.166] **SPRING ANTICIPATION**: Bônus de +20 pts e estilo STRIKE para ativos de Elite Mola em compressão, antecipando o volume institucional.
        - [V110.155] GENESIS INTEGRITY: Implementação de Genesis ID para rastreio atômico de ordens.
3.  **Doutrina Elite (V110.152)**:
    *   **ELITE STRIKE**: Sinais com **Score >= 92** são forçados como `STRIKE` se houver cruzamento técnico, bypassando a necessidade de Whale Tracker.
    *   **SPRING BYPASS**: Sinais com a flag `is_spring_strike` ignoram o `AmbushAgent` e validadores de preço, indo direto para a execução.
    *   **EXTERMINIO DE BLUE CHIPS & STABLECOINS**: BTC, ETH, SOL, BNB e todas as Stablecoins (USDE, USDC, etc.) são bloqueados ABSOLUTAMENTE. Nenhum agente (Blitz ou Swing) pode processar estes ativos. Foco 100% em ativos Elite 50x com flutuação real (ex: SUI, APT).
4.  **Bypass de Rigor Lateral**: Sinais marcados como `STRIKE` ou `SPRING STRIKE` possuem bypass total da Guilhotina Lateral (ADX < 20).
5.  **Score mínimo:** **>= 70** (Otimizado para liquidez — V110.149).
6.  **Timeframe:** **M30 exclusivo**.
7.  **Scan Cooldown:** **30 segundos**.

### Meta Operacional (The "10/Day" Goal)
- **Objetivo Primal:** **10 Gains por dia** (Trades finalizados com PnL > 0).
- **Monitoramento:** Acompanhamento via card unificado `RADAR DE INTELIGÊNCIA` no topo.
- **Progressiva:** Cada trade vencedor incrementa o contador diário e o ROI total de 24h.

---

## 4. RADAR DE INTELIGÊNCIA — FOCO DINÂMICO (V110.144)

**Arquivo:** `signal_generator.py::get_radar_pulse()`

### Lateral Throttle (Modo Anti-Poluição)
- **Gatilho:** BTC em mercado lateral (**ADX < 20**).
- **Ação:** Ocultar automaticamente todos os sinais de **SWING** com Score < 95.
- **Foco:** Prioridade visual total para sinais **BLITZ** (M30) em períodos de baixa volatilidade.

### Monitor de Metas RTDB
- **Injeção de Status:** O sistema injeta estatísticas de `daily_gains` e `daily_pnl` dentro do card unificado do Radar para manter o foco constante no alvo diário.

### Escadinha Step-Lock (1 Unidade por degrau)
| ROI atingido  | SL travado em | Acao                           | Unidades garantidas |
|---------------|---------------|--------------------------------|---------------------|
| >= breakeven* | +6.0% ROI      | Break-Even Adaptativo          | 0                   |
| >= 70%        | +50% ROI       | Risk-Zero                      | 0                   |
| >= 100%       | +95% ROI      | UNIT 1 LOCKED                  | 1                   |
| >= 200%       | +180% ROI     | UNIT 2 LOCKED                  | 2                   |
| >= 300%       | +270% ROI     | UNIT 3 LOCKED + Avalia Moonbag | 3                   |

*Breakeven Adaptativo via Librarian DNA:
- SMOOTH/JUMPY wick: breakeven em 30% ROI
- wick_multiplier >= 2.0: breakeven em 50% ROI
- wick_multiplier >= 3.0 ou is_retest_heavy: breakeven em 60% ROI

**Hard Stop software:** -80% ROI (~1.6% preco @ 50x)
**Arquivo:** `execution_protocol.py::process_sniper_logic()` bloco `slot_type == "BLITZ_30M"`

---

## 5. SWING SNIPER — ESCADINHA (Slots 3-4)

**Arquivo:** `execution_protocol.py` bloco `slot_type in [TREND, SWING, ...]`

| ROI atingido              | SL travado em | Acao                         |
|---------------------------|---------------|------------------------------|
| >= breakeven_trigger*     | +6.0% ROI     | Break-Even                   |
| >= 50%                    | +25% ROI      | Profit Bridge                |
| >= 70%                    | +45% ROI      | Risk-Zero                    |
| >= 110%                   | +80% ROI      | Profit Lock                  |
| >= 150%                   | +110% ROI     | EMANCIPACAO (Moonbag)        |
| >= 500%                   | +350% ROI     | MOONBAG ESCADINHA            |
| >= 800%                   | +600% ROI     | CHOKE-HOLD DYNAMIC           |
| >= 1000%                  | +850% ROI     | GALAXY MODE (90% Harvest)    |
| >= 1200%                  | +1000% ROI    | DIAMOND HANDS (Final Target) |

*breakeven_trigger = 30% padrao, 36% para RETEST_HEAVY, 50% para wick extremo

*breakeven_trigger = 30% padrao, 36% para RETEST_HEAVY, 50% para wick extremo

---

## 6. LEVERAGE — QUARTERMASTER

**Arquivo:** `quartermaster.py::check_armory()`

| Wick Intensity | Classe  | Leverage | Margin Multiplier |
|----------------|---------|----------|-------------------|
| < 0.45         | SMOOTH  | 50x      | 1.0x              |
| 0.45 a 0.70    | JUMPY   | 20x      | 2.5x              |
| >= 0.70        | EXTREME | 10x      | 5.0x              |

**Bloqueio automatico:** EXTREME + ADX < 25 = ordem bloqueada
**REGRA:** Blitz IGNORA o Quartermaster (50x sempre). Swing usa o Quartermaster.

---

## 7. FILTROS DE ENTRADA — CAPTAIN

**Arquivo:** `captain.py::monitor_signals()`

### Filtro 1: ADX Macro (Guilhotina Lateral)
- Se ADX < 20: BLOQUEIA (Swing/Structural) — EXCETO:
  - `is_blitz = True` -> bypass automatico (BLITZ-PRIORITY)
  - [V110.148] Bloqueio absoluto para Swing (Elite/Whale bypass removido para evitar falhas em laterais)

### Filtro 2: Vanguard Quality
- Se nectar_seal contem "VANGUARD" E score < 80: BLOQUEIA — EXCETO:
  - `is_blitz = True` -> bypass automatico

### Filtro 3: TRAP Shield & Trap-Prone Shield (ABSOLUTO — EXCETO MOLAS)
- Se nectar_seal contem "TRAP": BLOQUEIA SEMPRE E ABORTA IMEDIATAMENTE (approved = False)
- [V110.149] Se `is_trap_prone` no DNA for True: BLOQUEIA SUMARIAMENTE — **EXCETO:**
  - `is_spring = True` (MOLA) -> **SPRING-BYPASS ATIVO**. Molas de elite podem ter pavios; a explosão compensa o risco.
- Se a tendência macro institucional atuar com DISTRIBUTION (para compras) ou ACCUMULATION (para vendas): BLOQUEIA COMPLETAMENTE (Whale Bias Divergence)
- [V110.173] Sinais de Mola possuem bypass do `ADX < 18` e `is_trap_prone`.

### Filtro 4: Quartermaster Block
- EXTREME wick + ADX < 25: BLOQUEIA
- Blitz nao passa pelo Quartermaster (leverage ja eh fixo no sinal)

### Filtro 5: Collision Guard (V110.137)
- Se ativo ja esta em qualquer slot ativo (qualquer direcao): BLOQUEIA
- Se ativo esta no Moonbag Vault: BLOQUEIA
- **SEM BYPASS** — nem Blitz pode abrir contra um Swing ativo no mesmo ativo

---

## 8. GESTAO DE RISCO — BANKROLL

**Arquivo:** `bankroll.py`

- Margem por slot: **10% da banca** (`margin_per_slot = 0.10`)
- Max slots simultaneos: **4** (`MAX_SLOTS` em settings)
- Anti-zombie cooldown: **120s** apos fechamento
- Inertia Shield (duplicate guard): **120s** entre aberturas do mesmo ativo
- Hard Stop ROI: **-80%** (`HARD_STOP_ROI` em execution_protocol.py)

---

## 9. MOONBAG (EMANCIPACAO E TRAILING)

**Arquivo:** `firebase_service.py::promote_to_moonbag()`, `execution_protocol.py`, `harvester.py`

- Gatilho SWING: **150% ROI** (Slots 3-4 apenas)
- Gatilho BLITZ: **Condicional** (pos 300% ROI, via Ceifeiro)
- Entry price = 0 bloqueia promocao (DATA INTEGRITY GUARD — F3)
- Trailing stop comeca em: **160% ROI** (era 200% antes do fix F4)
- **[V110.138] CHOKE-HOLD DYNAMIC:** A partir de 800% ROI, o Stop Loss abandona os degraus fixos e fica dinamicamente preso a exatos **-150%** de distância do topo atual.
- **[V110.138] PARABOLIC CLIMAX:** Se ROI ultrapassar 1000% e o ativo demonstrar exaustão de Momentum (RSI > 85), o Ceifeiro liquida 90% a mercado (God-Candle Harvest).
- Emancipacao falha -> ROLLBACK de estado para retry automatico (F1)
- Colecao Firestore: `moonbags`
- RTDB path: `moonbag_vault`

---

## 10. HIERARQUIA DE AGENTES (NAO ALTERAR SEM REVISAO TOTAL)

```
Captain (orquestrador central)
  ├── BlitzSniper   -> Slots 1 e 2 (loop paralelo async, real-time M30 scan)
  ├── Oracle        -> Valida macro (ADX, BTC Pulse)
  ├── Librarian     -> DNA do ativo (Wick Intensity, NECTAR/TRAP, Breakeven Adaptativo)
  ├── Quartermaster -> Alavancagem e margem (ignorado pelo Blitz)
  ├── Ambush        -> Entrada de precisao (Spring Hunter / Tocaia)
  ├── Sentinel      -> Monitora SL progressivo (Escadinha)
  ├── Harvester     -> Saidas parciais e trailing stop (Moonbags + Moonbag Condicional Blitz)
  └── FleetAudit    -> Reconciliacao de estado (ghost cleanup REAL e PAPER)
```

**REGRA:** Nenhum agente deve depender diretamente da Bybit REST.
Bybit = responsabilidade do `bybit_rest.py`.
Agentes falam com o Captain ou com o Bankroll.

---

## 11. COLECOES FIREBASE — MAPA DE DADOS

| Colecao Firestore  | Proposito                                    |
|--------------------|----------------------------------------------|
| `slots_ativos`     | Estado dos 4 slots tatticos                  |
| `banca_status`     | Saldo, risco, slots disponiveis              |
| `trade_history`    | Historico Vault (UI visivel)                 |
| `vault_management` | Ciclo atual, PnL acumulado                   |
| `moonbags`         | Posicoes emancipadas                         |
| `orders_genesis`   | Passaporte imutavel de cada ordem (V110.137) |
| `trade_analytics`  | Logs internos (NAO apagar em reset leve)     |

| RTDB Path       | Proposito                         |
|-----------------|-----------------------------------|
| `live_slots`    | Espelho dos slots (UI tempo real) |
| `banca_status`  | Espelho da banca (UI)             |
| `moonbag_vault` | Espelho dos moonbags (UI)         |
| `vault_status`  | Resumo do ciclo (UI)              |
| `radar_pulse`   | Sinais e decisoes do radar        |

---

## 12. ARQUIVOS CRITICOS — RAIO DE EXPLOSAO

Se voce editar este arquivo...   ...revise tambem estes:
- `blitz_sniper.py`            -> `captain.py` (loop Blitz), `bankroll.py` (slot routing)
- `execution_protocol.py`      -> `captain.py` (process_sniper_logic), `bankroll.py`
- `bankroll.py::open_position` -> `captain.py`, `firebase_service.py` (genesis)
- `captain.py`                 -> Todos os agentes (hub central)
- `firebase_service.py`        -> `bankroll.py`, `vault_service.py`
- `quartermaster.py`           -> `captain.py` (check_armory call)
- `librarian.py`               -> `captain.py` + `execution_protocol.py` (breakeven blitz)
- `harvester.py`               -> `execution_protocol.py` (trailing start), `fleet_audit.py`
- `fleet_audit.py`             -> `bybit_rest.py` (paper_moonbags), `firebase_service.py`

---

## 13. CONSTANTES CRITICAS — NUNCA MUDAR SEM APROVACAO EXPLICITA

```python
# execution_protocol.py
HARD_STOP_ROI       = -80.0   # Limite absoluto de perda
V12_MAX_RISK_PCT    = 1.0     # Max risco por trade (%)
V12_STRUCTURAL_BUFFER = 2.5  # Buffer estrutural (%)
BLITZ_UNIT1_LOCK    = 95.0   # SL ao atingir 100% ROI
BLITZ_UNIT2_LOCK    = 180.0  # SL ao atingir 200% ROI
BLITZ_UNIT3_LOCK    = 270.0  # SL ao atingir 300% ROI
MOONBAG_TRAIL_START = 160.0  # ROI onde trailing stop comeca

# bankroll.py
margin_per_slot  = 0.10      # 10% da banca por slot
BLITZ_SLOTS      = [1, 2]    # Slots exclusivos do Blitz
SWING_SLOTS      = [3, 4]    # Slots exclusivos do Swing

# quartermaster.py
wick_smooth_threshold = 0.45
wick_jumpy_threshold  = 0.70
lev_smooth = 50  |  lev_jumpy = 20  |  lev_extreme = 10

# blitz_sniper.py
BLITZ_LEVERAGE   = 50        # Fixo, sem excecao
BLITZ_SCORE_MIN  = 70        # Score minimo (Otimizado V110.149)
BLITZ_TP_RR_MIN  = 2.0       # R:R minimo (TP = 2x SL_dist)
```

---

## 14. PROTOCOLO NUCLEAR (RESET DE BANCO DE DADOS)

**REGRA ESTRITA:** O estado atual do sistema sofre "Crash de Renderizacao" na UI se as regras abaixo nao forem seguidas milimetricamente durante um Wipe:

1. **Backend KILL:** NUNCA apague o banco de dados com o backend rodando. Execute `python TERMINAR_TUDO.py` antes.
2. **Slots Obrigam "id":** Um slot, mesmo "LIVRE", **PRECISA** ter o campo `"id": 1` (ou 2,3,4).
3. **Ghost Wipe Obligatorio:** Um script de Wipe real DEVE apagar `moonbags` e `orders_genesis` no Firestore, e `moonbag_vault` no RTDB.

---

## 14. DESIGN INVARIANTE — SEAMLESS GLASSMORHPISM (V110.171)
- **Estética:** Grayscale Premium (Preto, Branco, Cinza e Lima para lucros).
- **Seamless:** Proibido o uso de bordas sólidas (`border-t`, `border-b`, `border-r`, `border-l`) entre componentes principais.
- **Transição:** Transições entre seções devem ser feitas via `padding`, `gap` e `bg-gradient` sutis, nunca via linhas demarcatórias brancas.
- **Glassmorphism:** Uso obrigatório de `backdrop-blur-xl/2xl/3xl` em todos os painéis fixos (Header, NavBar, Modais).
- **Bordas:** Bordas são permitidas apenas em cards individuais (`SlotCard`, `RadarCard`) com opacidade baixa (`border-white/5` ou `border-white/10`).

---

## 15. V110.173: ELITE SPRING DOCTRINE 🌸 [APR 23]
- **Librarian Spring Audit:** Backtest de 15 dias (M30) identifica os 40 ativos mais explosivos pós-compressão.
- **Frota Unificada:** Blitz e Swing focam exclusivamente na `spring_elite_list` (40 pares). Monitoramento de 90+ pares foi descontinuado para reduzir latência e aumentar precisão.
- **Spring Shield (Bypass):** Sinais identificados como "Mola" (Spring) ignoram a Guilhotina Lateral (ADX < 18) e o Trap-Prone Shield tanto no Blitz quanto no Swing.
- **ROI 1.200%:** Escadinha de Swing expandida para alvos extremos (Diamond Hands), com proteção dinâmica de lucro (Choke-Hold) acima de 800% ROI.
- **Dynamic UI Sync:** Badges de estratégia no Cockpit são 100% dinâmicas, consumindo `strategy_label` do RTDB. IDs de slot fixos (1-4) não determinam mais o rótulo visual.

---

---

## 16. SINCRONIZAÇÃO DE UI E METADADOS (V110.173)
- **Arquivo:** `bankroll.py::open_position()`, `cockpit.html::SlotCard`
- **REGRA:** Toda abertura de ordem DEVE injetar `strategy` (BLITZ_30M/SWING) e `strategy_label` (ex: "BLITZ | SPRING") no RTDB.
- **REGRA:** O Cockpit UI deve renderizar a cor da badge baseada no `strategy`:
    - `BLITZ_30M` -> Branco (`bg-white text-black`)
    - `SWING` -> Âmbar (`bg-amber-500 text-white`)
- **REGRA:** A invisibilidade de texto em badges é estritamente proibida; use `font-size: 9px` e contraste absoluto.
- **Genesis ID:** UI `cockpit.html` deve exibir o selo `🧬 GENESIS: ID` logo abaixo do símbolo do ativo. 
- **Fallback de Identidade:** Caso o `genesis_id` esteja ausente (trades legados), o sistema deve exibir o `order_id` para manter a integridade do protocolo "Genesis Iron Lock".

---

## 17. V110.174: SELECTIVE INTELLIGENCE UPGRADE (VANGUARD) [APR 24]
- **Asset Trend Guard (H4):** Bloqueio obrigatório de operações contra a tendência H4 do próprio ativo em moedas de volatilidade `EXTREME`. 
- **Spring Direction Filter:** Sinais de "Mola" (Spring) só podem ignorar travas laterais se a direção do trade coincidir com a tendência H4 do ativo.
- **Trap-Prone Macro Shield:** Ativos classificados como `is_trap_prone` exigem um `Macro Score` mínimo de 60 para autorização de caçada.
- **Objetivo:** Aumentar a seletividade e evitar massacres em ativos altamente voláteis que ignoram sinais técnicos em favor da tendência macro.

---

*Versao: V110.174 "Selective Intelligence Upgrade" | Atualizado: 2026-04-24 | SPRING SHIELD REFORÇADO*
*Este arquivo e a FONTE DA VERDADE para edicoes de codigo.*
*Em caso de conflito com MASTER_ARCHITECTURE.md, ESTE arquivo prevalece.*
