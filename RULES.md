# RULES.md — 10D Sniper V110.350 "Protocolo Sniper Elite 20 Dashboard"
# Invariantes Tecnicas Inegociaveis — [PERSISTÊNCIA ABSOLUTA]
# Leia INTEIRO antes de tocar em qualquer arquivo.
# Fonte da verdade: codigo real no Railway e PostgreSQL/WebSocket Nativo.

---

## 🛡️ PROTOCOLO DE BLINDAGEM V4.0 (CRÍTICO)
1. **AUTO-CURA DE BANCO:** O sistema realiza migrações automáticas de esquema no boot. Qualquer divergência de coluna deve ser corrigida via script integrado ao `database_service.py`.
2. **TIMEZONE INTEGRITY (CRÍTICO):** É obrigatório o uso de `datetime.utcnow().replace(tzinfo=None)` ou `datetime.utcnow()` para todas as interações e comparações com o Postgres. **NUNCA** use `datetime.now(timezone.utc)` para comparações diretas com timestamps do banco, pois isso gera erro de "offset-naive vs offset-aware". SSOT: Naive UTC.
3. **ARQUIVAMENTO ATÔMICO:** É terminantemente proibido limpar um slot sem antes garantir o arquivamento no Postgres via `database_service.log_trade`.
4. **PAPER MODE ENFORCEMENT:** Em modo de teste, a variável `BYBIT_EXECUTION_MODE` deve ser injetada como `PAPER` no Railway para garantir o saldo simulado de $100.
5. **META DE LUCRO ROI >= 80% (V110.350):** O contador de progresso diário (Dashboard) e o contador de ciclos do Vault (1/10) agora são baseados em ROI técnico (>= 80%) em vez de lucro fixo em dólar. Isso garante a justiça do ciclo independente do capital (Compound-Ready).

---

## REGRA 00 — REPOSITÓRIO ÚNICO E OFICIAL
1. **REPO ÚNICO:** O único repositório oficial e absoluto para este sistema é: `https://github.com/JonatasOliveira1983/10D5.0/`.
2. **PUSH OBRIGATÓRIO:** Todo commit deve ser enviado exclusivamente para o branch `main` do repositório `10D5.0` para deploy automático.
3. **EXTINÇÃO DE REPOS ANTIGOS:** O repositório `10DBybityREAL` está EXTINTO e não deve ser utilizado.
4. **URL DE COMANDO:** A UI oficial é acessível via `https://1crypten.space/`.

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
- **REGRA (COLLISION GUARD):** Impede o mesmo ativo em mais de um slot simultaneamente via `paper_positions` e Postgres.
- **REGRA (DEMANDA ADAPTATIVA - V110.350):** O sistema monitora as vagas nos slots em tempo real. Se os slots de um tipo (Blitz ou Swing) estiverem cheios, a busca por sinais desse tipo é SUSPENSA. Se os 4 slots estiverem cheios, os agentes Visão e Radar entram em STANDBY total para economizar créditos de IA até que ocorra uma liberação de vaga.

---

## 2. GENESIS ID — PASSAPORTE DA ORDEM
- **Geração Instantânea:** O `genesis_id` é gerado no momento do nascimento da ordem, inclusive em Paper Mode.
- **Formato Atômico:** `BLZ-{UUID6}-{SYM4}` (Blitz) / `SWG-{UUID6}-{SYM4}` (Swing)
- **REGRA:** O `genesis_id` é persistido no **PostgreSQL** e transmitido via **WebSocket** imediatamente.
- **REGRA:** genesis_id deve acompanhar a ordem até o fechamento.

---

## 3. SNIPER PONTO 3 & ELITE 20 FOCUS (V110.350)
1. **Foco 20 Elite:** O sistema monitora exclusivamente os 20 melhores pares selecionados pelo Bibliotecário. Sinais fora dessa lista são ignorados para garantir foco absoluto.
2. **Gatilho Sniper Ponto 3 (M30):** Todas as entradas são baseadas no padrão 1-2-3 em tempos gráficos de 30 minutos.
3. **Paciência do Sniper (Vio-Hunter):** O `AmbushAgent` aguarda a rejeição no Ponto 3 (pavios longos) antes de disparar.
4. **Deep Dive Logging:** A cada 10 minutos, o sistema emite um log detalhado (`📊 [ELITE-SCAN]`) com CVD, RSI, Trend e Regime de todos os 20 pares monitorados para auditoria completa.

---

## 4. RADAR DE INTELIGÊNCIA — DASHBOARD V110.350
- **MarketRadarWidget (UI):** O dashboard utiliza agora um container fixo de 5 slots para sinais de elite. Isso garante estabilidade visual (sem "pulos" de layout) tanto no Mobile quanto no Desktop.
- **Deduplicação de Sinais:** O radar processa e consolida sinais duplicados do mesmo ativo, exibindo apenas o sinal mais recente e de maior score.
- **Blindagem contra Crashes:** Todos os símbolos na UI são tratados com `optional chaining` e fallbacks para evitar erros de renderização (`TypeError: undefined`).

---

## 5. ORÁCULO DE MERCADO — ESTABILIZAÇÃO ÁGIL
- **Boot Time:** Reduzido para **15-30 segundos** no Railway.
- **Fallback ADX:** Se o Oráculo estiver estabilizando, o sistema usa o ADX bruto do WebSocket para não travar o Radar.

---

## 6. GESTÃO DE RISCO — BANKROLL RAILWAY
- **Banca Padrão:** **$100.00** (Simulado/Paper).
- **Margem por slot:** **10% da banca** ($10.00 por ordem).
- **Protocolo de Reset Nuclear:** O endpoint `/api/system/nuclear-reset` permite a limpeza total do banco, histórico e reset da banca para $100 em um único comando atômico.

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
4. **VISUALIZAÇÃO TÉCNICA (ESCADINHA ELITE):** O gráfico do cockpit deve renderizar obrigatoriamente as 5 linhas de alvo da estratégia Sniper: T1(30%), T2(50%), T3(70%), T4(110%) e T5(150%).
5. **PRECISÃO DE PNL:** O cálculo do ROI na interface deve utilizar o feed de preço do WebSocket (BybitWS) para evitar disparidades visuais com o gráfico.

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
3. **Veto Obrigatório Universal:** O **Agente Visão** e o **Bibliotecário** continuam sendo filtros OBRIGATÓRIOS. Se todos os modelos da cascata falharem, a ordem é bloqueada por segurança (`[VISION-OFFLINE-BLOCK]`).

---

## 13. OBSERVATORY (VISUAL HQ) & VISION INTELLIGENCE (V5.6)
1. **Motor Proprietário (S3):** O sistema utiliza uma engine de gráficos nativa (Lightweight Charts), eliminando 100% da dependência de iframes externos (TradingView) e resolvendo erros de CSP.
2. **Master Context Layout:** O Observatório opera em uma arquitetura de 3 andares sincronizados.
3. **Captura Autônoma:** O `ScreenshotService` captura exclusivamente o Hub Proprietário.

---

*Versão: V110.350 "Elite 20 Sniper Protocol - Dashboard Update" | Atualizado: 2026-04-28*
*Este arquivo é a ÚNICA FONTE DA VERDADE. Repositório Oficial: 10DBybityREAL.*
