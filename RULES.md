# RULES.md — 10D Sniper V110.300 "Protocolo Sniper Elite 20"
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
- **REGRA:** Slots 1 e 2 são EXCLUSIVOS para BlitzSniper (30M). Slots 3 e 4 para Swing e Moonbags.
- **REGRA (MOONBAG EXPANSION):** Se uma Moonbag ocupar um slot de Swing, o sistema libera o slot lógico para um novo par da lista Elite, mantendo sempre o processamento focado nos 20 pares ativos.
- **REGRA:** Collision Guard impede o mesmo ativo em mais de um slot simultaneamente via `paper_positions` e Postgres.

---

## 2. GENESIS ID — PASSAPORTE DA ORDEM
- **Geração Instantânea:** O `genesis_id` é gerado no momento do nascimento da ordem, inclusive em Paper Mode.
- **Formato Atômico:** `BLZ-{UUID6}-{SYM4}` (Blitz) / `SWG-{UUID6}-{SYM4}` (Swing)
- **REGRA:** O `genesis_id` é persistido no **PostgreSQL** e transmitido via **WebSocket** imediatamente.
- **REGRA:** genesis_id deve acompanhar a ordem até o fechamento.

---

## 3. SNIPER PONTO 3 & ELITE 20 FOCUS (V110.300)
1. **Foco 20 Elite:** O sistema monitora exclusivamente os 20 melhores pares selecionados pelo Bibliotecário. Sinais fora dessa lista são ignorados para garantir foco absoluto.
2. **Gatilho Sniper Ponto 3 (M30):** Todas as entradas são baseadas no padrão 1-2-3 em tempos gráficos de 30 minutos.
   - (1) Pivot Inicial. (2) Sweep de Liquidez. (3) Rejeição/Confirmação (Mínima/Máxima Protegida).
3. **Paciência do Sniper (Vio-Hunter):** O `AmbushAgent` aguarda a rejeição no Ponto 3 (pavios longos) antes de disparar.
4. **Take Profit Sniper:** Expansão de Fibonacci (1:2 ou 1:3) do movimento 1-2.
5. **Stop Loss Técnico:** Posicionado obrigatoriamente abaixo (Long) ou acima (Short) do Ponto 3 do padrão.

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

## 13. OBSERVATORY (VISUAL HQ) & VISION INTELLIGENCE (V5.6)
1. **Motor Proprietário (S3):** O sistema utiliza uma engine de gráficos nativa (Lightweight Charts), eliminando 100% da dependência de iframes externos (TradingView) e resolvendo erros de CSP.
2. **Master Context Layout:** O Observatório opera em uma arquitetura de 3 andares sincronizados:
   - **Andar 1 (Price Action):** Candles + SMA 21/100 + SuperTrend + Ghost Markers.
   - **Andar 2 (Volume Flow):** Histograma de volume puro e destacado.
   - **Andar 3 (RSI 14):** Oscilador de força relativa para detecção de exaustão.
3. **Global BTC HUD:** Uma barra fixa no topo transmite a telemetria mestre do mercado (Preço BTC, ADX, CVD, Dominância, Decorrelação e Direção Master) para todas as análises.
4. **Ghost Markers (Treinamento de IA):** O sistema injeta marcadores históricos de "Entrada Perfeita" e "Rejeição" para que o Agente Visão aprenda com padrões de sucesso passados.
5. **Captura Autônoma:** O `ScreenshotService` captura exclusivamente o Hub Proprietário, garantindo que a IA analise exatamente os mesmos indicadores que o operador humano.

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
1. **ELITE_20_MATRIX é a única fonte de ativos.** Tanto o BlitzSniper quanto o SignalGenerator operam **exclusivamente** sobre os 20 pares de elite.
2. **BTC é referência, não alvo.** O `BTCUSDT.P` é monitorado para contexto mas nunca é operado.
3. **Reset de Sistema (Estado Zero):** O script `fresh_start.py` é o protocolo oficial para reset de banca ($100), ciclos da Vault e purgação de histórico para novos ciclos operacionais.
4. **Slot-Type explícito:** Sinais Ponto 3 são classificados como BLITZ (Slots 1-2) ou SWING (Slots 3-4) pelo Agente Visão com base na força da confluência.
5. **Verbosidade Tática:** O Bibliotecário deve emitir o "Relatório Tático Foco 20" a cada ciclo de scan para auditoria visual em tempo real.

### 14.3 Identificadores de Sinal para Diagnóstico nos Logs
- `⚡ [BLITZ-MATRIX]` → BlitzSniper usando SPECIALIST_MATRIX corretamente
- `⚡ [BLITZ-MATRIX-FALLBACK]` → BlitzSniper em fallback (Bibliotecário ainda inicializando)
- `⚓ [V4.2 SLOT-ROUTING] ... → Slot Type: BLITZ_30M` → Capitão roteando para Slots 1&2
- `⚓ [V4.2 SLOT-ROUTING] ... → Slot Type: SWING` → Capitão roteando para Slots 3&4
- `🚫 [MATRIX-VETO]` → Ativo rejeitado por não estar na SPECIALIST_MATRIX

---

---

## 15. ESTRATÉGIA 1-2-3 (ALTA PRECISÃO) — [V5.6]
1. **Definição Visual:**
   - **(1) Pivot Inicial:** Fundo ou Topo isolado.
   - **(2) Sweep/Extremo:** Mínima menor que (1) para Longs, ou Máxima maior que (1) para Shorts. Representa a captura de liquidez.
   - **(3) Confirmação:** Fundo mais alto que (2) para Longs, ou Topo mais baixo que (2) para Shorts.
2. **Gatilho de Strike (Strike Zone):** O rompimento da máxima (Long) ou mínima (Short) entre os pontos 2 e 3. Marcado no Observatório com uma **linha horizontal tracejada branca**.
3. **Filtro de Visão:** O Agente Visão deve validar se o preço está "reagindo" no Ponto 3 com pavios ou volume antes de aprovar a ordem.

---

*Versão: V110.300 "Elite 20 Sniper Protocol" | Atualizado: 2026-04-28*
*Este arquivo é a ÚNICA FONTE DA VERDADE. Repositório Oficial: 10DBybityREAL.*
