import logging
import asyncio
import time
from typing import Dict, Any, List
from services.agents.aios_adapter import AIOSAgent
from services.sovereign_service import sovereign_service

logger = logging.getLogger("OracleAgent")

class OracleAgent(AIOSAgent):
    def __init__(self):
        super().__init__(
            agent_id="agent-oracle-v1",
            role="oracle",
            capabilities=["market_integrity", "amnesia_guard", "data_validation"]
        )
        self.boot_time = time.time()
        self.stabilization_period = 30 # [V110.175] Reduzido para 30s (mais ágil no Railway)
        self.market_context = {
            "regime": "TRANSITION",
            "btc_direction": "NEUTRAL",
            "btc_adx": 20.0,
            "btc_price": 0.0,
            "btc_variation_1h": 0.0,
            "btc_variation_24h": 0.0,
            "btc_variation_15m": 0.0,
            "dominance": 50.0,
            "status": "BOOTING",
            "is_stale": False,
            "last_updated": time.time(), # [V110.175] Evita STALE imediato
            "remaining_wait": 30
        }
        self.last_save_time = 0
        self._is_initialized = False

    async def initialize(self):
        if self._is_initialized: return
        
        # 🟢 Railway Sovereign Mode: Booting directly
        logger.info("🔮 [ORACLE] Sovereign Boot: Data Integrity monitoring ACTIVE.")
        self.market_context["status"] = "BOOTING"
        
        self._is_initialized = True
        logger.info("🔮 Oracle Agent Initialized & Watching Data Integrity.")
        asyncio.create_task(self.run_loop())

    async def on_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        msg_type = message.get("type")
        if msg_type == "GET_CONTEXT":
            return {"status": "SUCCESS", "data": self.get_validated_context()}
        return {"status": "ERROR", "message": "Unknown type"}

    def get_validated_context(self) -> Dict[str, Any]:
        """Returns the validated context with security rigor check (2-3 min wait)."""
        now = time.time()
        uptime = now - self.boot_time
        
        # 🛡️ Rigor de Segurança: 2-3 min de espera após boot
        if uptime < self.stabilization_period:
            self.market_context["status"] = "STABILIZING"
            self.market_context["remaining_wait"] = int(self.stabilization_period - uptime)
            # Durante estabilização, os dados podem estar vindo do LKG ou brutos, mas status é STABILIZING
            # Isso impede que o Captain/Guardian tomem decisões até o fim do período.
        else:
            self.market_context["remaining_wait"] = 0
            # Check staleness (5 min)
            if (now - self.market_context["last_updated"]) > 300:
                self.market_context["status"] = "STALE_DATA"
                self.market_context["is_stale"] = True
            elif self.market_context.get("btc_adx", 0) <= 0.01:
                self.market_context["status"] = "ERROR_ZERO_ADX"
                self.market_context["is_stale"] = True
            else:
                self.market_context["status"] = "SECURE"
                self.market_context["is_stale"] = False
                
        return self.market_context

    async def update_market_data(self, source: str, data: dict):
        """Receives data from sources (BybitWS, SignalGenerator, MacroAnalyst)."""
        now = time.time()
        
        # 🛡️ Data Sanitization
        if "btc_adx" in data:
            new_adx = float(data["btc_adx"])
            
            # [AMNESIA-FIX] Reject Zero ADX entirely
            if new_adx <= 0.01:
                logger.warning(f"🔮 [ORACLE] Rejecting ZERO ADX Update: {new_adx}")
                del data["btc_adx"] # Remove to not update
            # [AMNESIA-FIX] Reject suspicious drops from relevant ADX to near 0
            elif self.market_context["btc_adx"] > 20 and new_adx < 10 and (now - self.boot_time > 60):
                 logger.warning(f"🔮 [ORACLE] Rejecting SUSPICIOUS ADX Drop: {self.market_context['btc_adx']} -> {new_adx}")
                 del data["btc_adx"]

        # Update core metrics
        for k, v in data.items():
            if k in self.market_context:
                self.market_context[k] = v
        
        self.market_context["last_updated"] = now
        self.market_context["last_source"] = source
        
        # [V110.62] CRASH DETECTION (Guardian Hedge Trigger)
        var_15m = data.get("btc_variation_15m", 0)
        if var_15m < -2.0: # Queda de 2% em 15 min = Pânico
            logger.warning(f"🚨 [ORACLE-PANIC] Queda violenta detectada: {var_15m:.2f}% em 15m. Disparando Guardian Hedge!")
            try:
                from services.bankroll import bankroll_manager
                asyncio.create_task(bankroll_manager.activate_emergency_hedge(reason=f"Flash Crash: {var_15m:.2f}% in 15m"))
            except Exception as e:
                logger.error(f"Erro ao disparar Hedge: {e}")
        elif var_15m > -0.5: # Recuperação ou estabilização
             try:
                from services.bankroll import bankroll_manager
                if getattr(bankroll_manager, 'hedge_active', False):
                    asyncio.create_task(bankroll_manager.auto_close_hedge(reason="Market Stabilized"))
             except Exception:
                 pass

    async def run_loop(self):
        """Monitor loop (Railway Sovereign Mode)."""
        while True:
            # Oracle Intelligence Loop (Placeholder for future local integrity checks)
            await asyncio.sleep(60)

# Singleton instance
oracle_agent = OracleAgent()
