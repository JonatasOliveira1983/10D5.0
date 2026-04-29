# RULES.md — 10D Sniper V110.403 "Industrial Process Vigilance"
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
14. **INTEGRIDADE DE FECHAMENTO (V110.360):** É obrigatório que o `BankrollManager` registre todas as ordens detectadas como fechadas (inclusive órfãs) no `trade_history` para garantir paridade absoluta entre a banca e o histórico auditável.
15. **NORMALIZAÇÃO DE SIDE (V110.360):** Todas as comparações de lado de ordem (`side`) no frontend e backend devem ser normalizadas (`toUpperCase()`) para suportar variações de API (Buy/BUY/LONG).
16. **INTELIGÊNCIA DO RADAR (V110.370):** O Radar deve operar de forma contextual. Se não houver slots disponíveis para um determinado tipo de estratégia (Blitz ou Swing), os sinais desse tipo devem ser filtrados na UI para evitar poluição visual e confusão operacional. O cabeçalho do Radar deve exibir a demanda ativa (ex: "VISÃO BUSCANDO 1 SWING").
17. **VISUAL FLOW SENTINEL (V110.371):** A "Linha Vertical" de scan nos gráficos é o indicador visual do agente Flow Sentinel. Ela deve refletir o status do sistema (Verde/Branco = Ativo, Vermelho = Falha de Integridade/Offline). Marcadores de "ENTRY" devem ser baseados no timestamp real (`opened_at`) para garantir precisão absoluta na auditoria visual.

---

## REGRA 00 — REPOSITÓRIO ÚNICO E OFICIAL
1. **REPO ÚNICO:** O único repositório oficial e absoluto para este sistema é: `https://github.com/JonatasOliveira1983/10D5.0/`.
2. **PUSH OBRIGATÓRIO:** Todo commit deve ser enviado exclusivamente para o branch `main` do repositório `10D5.0` para deploy automático.
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
- **REGRA (COLLISION GUARD):** Impede o mesmo ativo em mais de um slot simultaneamente via `paper_positions` e Postgres.
- **REGRA (DEMANDA ADAPTATIVA - V110.370):** O sistema monitora as vagas nos slots em tempo real. O Radar agora filtra sinais para exibir apenas os tipos compatíveis com as vagas abertas. Se os 4 slots estiverem cheios, o Radar entra em modo STANDBY automático.

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

## 4. RADAR DE INTELIGÊNCIA — DASHBOARD V110.370
- **MarketRadarWidget (UI):** O dashboard utiliza agora um container fixo de 5 slots para sinais de elite. Isso garante estabilidade visual (sem "pulos" de layout) tanto no Mobile quanto no Desktop.
- **Deduplicação de Sinais:** O radar processa e consolida sinais duplicados do mesmo ativo, exibindo apenas o sinal mais recente e de maior score.
- **Filtro de Demanda Ativa:** O Radar deve priorizar e exibir apenas sinais que correspondam aos slots vazios. Se não houver vaga para BLITZ, o Radar oculta sinais BLITZ.
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

## 12. INTELIGÊNCIA COLETIVA E AGENTE VISÃO (V110.403 — VIGILÂNCIA INDUSTRIAL & CACHE)
1. **Vision Gate Seletivo:** O Agente Visão só captura screenshots e aciona a IA se o sinal tiver **Score >= 95** (Captain) ou **Confidence >= 90** (Librarian). Sinais secundários são processados via quantitativo puro.
2. **Protocolo de Demanda Ativa:** O Bibliotecário só invoca a Visão se houver slots livres para o tipo de estratégia (Blitz vs Swing). Se o sistema estiver 4/4, entra em **Standby de Inteligência**.
3. **Análise de Cache (TTL 15m):** Resultados visuais são memorizados por 15 minutos por ativo. Se o sinal persistir sem mudança estrutural, o sistema reutiliza a decisão anterior para economizar quota.
4. **Veto Obrigatório Universal:** Se o score for >= 95, o Visão tem poder de veto. Inclui backoff de 1h para quota excedida no Gemini.

---

## 13. OBSERVATORY (VISUAL HQ) & VISION INTELLIGENCE (V5.6)
1. **Motor Proprietário (S3):** O sistema utiliza uma engine de gráficos nativa (Lightweight Charts), eliminando 100% da dependência de iframes externos (TradingView) e resolvendo erros de CSP.
2. **Master Context Layout:** O Observatório opera em uma arquitetura de 3 andares sincronizados.
3. **Captura Autônoma:** O `ScreenshotService` captura exclusivamente o Hub Proprietário.

---

*Versão: V110.403 "Industrial Process Vigilance" | Atualizado: 2026-04-30*
*Este arquivo é a ÚNICA FONTE DA VERDADE. Repositório Oficial: 10D5.0.*

