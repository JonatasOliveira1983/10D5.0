# 1CRYPTEN_SPACE_V4.0 - V110.12.5 ENFORCED SHADOW
import sys
import codecs
if sys.platform == "win32":
    try:
        # V89.6: Force UTF-8 encoding for Windows console to prevent UnicodeEncodeError with emojis
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python versions if reconfigure is missing
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import traceback
import os
import datetime
import asyncio
import logging
import time
from fastapi import FastAPI, Depends, HTTPException, Header, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

class ManualChatRequest(BaseModel):
    text: str

from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
import uvicorn
import ssl
import urllib3
from services.kernel.dispatcher import kernel
from config import settings
from concurrent.futures import ThreadPoolExecutor
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

# V15.1 Fix: Custom Middleware to prevent index.html caching
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            response = await call_next(request)
            if request.url.path in ["/", "/index.html", "/banca", "/radar", "/chat", "/vault", "/config"]:
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, proxy-revalidate"
                # V110.30.1: Hardened Cache Blindness
                response.headers["Pragma"] = "no-cache"
                response.headers["Expires"] = "0"
                response.headers["Surrogate-Control"] = "no-store"
            return response
        except Exception as e:
            logger.error(f"❌ ASGI Middleware Exception during {request.url.path}: {str(e)}")
            from fastapi.responses import JSONResponse
            # V110.30.1: Shield Protection - instead of crashing uvicorn, we return a 500 JSON
            return JSONResponse(
                status_code=500,
                content={"status": "error", "message": "Internal Server Shield: Route Failed", "path": request.url.path}
            )

# V5.2.4.6: Increase Thread Pool size for concurrent network calls
executor = ThreadPoolExecutor(max_workers=32)
asyncio.get_event_loop().set_default_executor(executor)

# V5.2.4.8 Cloud Run Startup Optimization - Infrastructure Protocol
# V90.3: PROTOCOLO COCKPIT - FIM DO CACHE
# V110.40.0: PROTOCOLO COMMAND CENTER PRO - ALMIRANTE ELITE
VERSION = "V110.200"
DEPLOYMENT_ID = "V110.200_SOVEREIGN_RESET"

# Global Directory Configurations - Hardened for Docker/Cloud Run
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Standard: backend/main.py -> ../../frontend
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "frontend"))
if not os.path.exists(FRONTEND_DIR):
    # Fallback to current dir if not found (mostly for cloud deployments)
    FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Global references
sovereign_service = None
database_service = None # V110.175
websocket_service = None # V110.175
bybit_rest_service = None
bybit_ws_service = None
bankroll_manager = None
redis_service = None
captain_agent = None  # V12.2: Standardized global
globals()['sig_gen'] = None        # V12.2: Standardized global
globals()['oracle_agent'] = None   # V110.32.1: Oracle Global

import logging.handlers
# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.handlers.RotatingFileHandler(
            os.path.join(BASE_DIR, "backend_v110_173.log"),
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
    ]
)
logger = logging.getLogger("1CRYPTEN-MAIN")
logger.info(f"BASE_DIR: {BASE_DIR}")
logger.info(f"FRONTEND_DIR: {FRONTEND_DIR}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # V5.2.0: Stability Staggering
    logger.info(f"Initializing 1CRYPTEN SPACE {VERSION}...")
    
    async def start_services():
        global sovereign_service, bybit_rest_service, bybit_ws_service, bankroll_manager, redis_service, captain_agent, sig_gen
        
        logger.info("Step 0: Loading services (slow-walk mode)...")
        try:
            import importlib
            # Load services with 1s delay each to keep event loop breathing
            logger.info("Step 0.1: Loading Sovereign Service...")
            sovereign_service = importlib.import_module("services.sovereign_service").sovereign_service
            
            logger.info("Step 1: Activating Sovereign Mode (Railway)...")
            await sovereign_service.initialize()

            logger.info("Step 1.1: Connecting Postgres (Railway)...")
            database_service = importlib.import_module("services.database_service").database_service
            await database_service.initialize()
            
            # [V110.208] AUTO-MIGRATION SHIELD: Ensures DB schema is always up to date
            try:
                from migrate_db import migrate
                await migrate()
                logger.info("✅ Database Schema check complete.")
            except Exception as migrate_err:
                logger.error(f"⚠️ Auto-migration failed, but continuing: {migrate_err}")

            logger.info("Step 1.2: Initializing WebSocket Service...")
            websocket_service = importlib.import_module("services.websocket_service").websocket_service
            
            logger.info("Step 0.1.1: Connecting Redis Service...")
            redis_service = importlib.import_module("services.redis_service").redis_service
            await redis_service.connect()
            await asyncio.sleep(1)
            
            logger.info("Step 0.2: Loading Bybit REST Service...")
            bybit_rest_service = importlib.import_module("services.bybit_rest").bybit_rest_service
            # V5.2.4.3: Added 30s timeout for Bybit initialization (includes time sync)
            await asyncio.wait_for(bybit_rest_service.initialize(), timeout=30.0)
            await asyncio.sleep(1)
            
            logger.info("Step 0.3: Loading Bybit WS Service...")
            bybit_ws_service = importlib.import_module("services.bybit_ws").bybit_ws_service
            await asyncio.sleep(0.5) # [V110.50] Reduced stagger for faster Cold Boot
            
            # Use bankroll_manager from services.bankroll
            logger.info("Step 0.4: Loading Bankroll Manager...")
            mod = importlib.import_module("services.bankroll")
            bankroll_manager = mod.bankroll_manager
            
            await asyncio.sleep(1)
            logger.info("Step 0: Service modules loaded \u2705")
            
            # [V110.6.3] EMERGENCY DEEP SCRUB TRIGGERED!
            if os.getenv("FACTORY_RESET_V110") == "TRUE":
                logger.warning("💥 [V110.6.3] EMERGENCY DEEP SCRUB TRIGGERED!")
                try:
                    from services.bybit_rest import bybit_rest_service
                    # 1. Clear RAM Positions
                    bybit_rest_service.paper_positions.clear()
                    # 2. Delete Persistent Paper State
                    if os.path.exists(bybit_rest_service.PAPER_STORAGE_FILE):
                        try: os.remove(bybit_rest_service.PAPER_STORAGE_FILE)
                        except: pass
                    # 3. Nuclear Reset Bankroll
                    await bankroll_manager._force_paper_reset_v110()
                    # 4. Clear Firebase Slots (Deep Cleaned in V110.6.3)
                    for i in range(1, 5):
                        try: await sovereign_service.free_slot(i, "[V110.6.3] FACTORY RESET TRIGGERED")
                        except: pass
                    logger.info("✅ [V110.6.3] EMERGENCY DEEP SCRUB EXECUTED SUCCESSFULLY! 💥")
                except Exception as e:
                    logger.error(f"❌ [V110.6.3] DEEP SCRUB FAILED: {e}")

            
            logger.info("Step 2: Syncing Bybit Instruments...")
            symbols = ["BTCUSDT.P", "ETHUSDT.P", "SOLUSDT.P"]
            try:
                # Fetch symbols in background
                async def fetch_and_start_ws():
                    try:
                        # [V110.173] Usar get_elite_focus_pairs para concentrar nos Top 40
                        s = await asyncio.wait_for(
                            bybit_rest_service.get_elite_focus_pairs(),
                            timeout=90
                        )
                        if s: await bybit_ws_service.start(s)
                    except Exception as e: 
                        logger.error(f"Step 2: Symbol Scan or WS Start Error: {e}")
                        await bybit_ws_service.start(symbols)
                asyncio.create_task(fetch_and_start_ws())
                # [V110.202] Force slot sync on startup - ensuring persistence during deploys
                logger.info("📡 [V110.202] Syncing slots from persistence layer...")
                await bankroll_manager.update_banca_status()
            except Exception as e:
                logger.warning(f"Step 2: Symbol fetch scheduled (Background): {e}")

            logger.info("Step 3: Activating Agents...")
            try:
                from services.agents.captain import captain_agent as captain_module
                from services.signal_generator import signal_generator as sig_gen_module
                
                # Assign to globals defined at module level
                globals()['captain_agent'] = captain_module
                globals()['sig_gen'] = sig_gen_module
                
                from services.agents.fleet_audit import fleet_audit
                
                from services.agents.macro_analyst import macro_analyst
                from services.agents.whale_tracker import whale_tracker
                from services.agents.onchain_whale_watcher import on_chain_whale_watcher
                from services.agents.sentiment_specialist import sentiment_specialist
                from services.agents.librarian import librarian_agent
                from services.agents.harvester import harvester_agent
                from services.agents.blitz_sniper import blitz_sniper_agent # [V110.137] Blitz Active

                
                # 🆕 [V110.32.1] Oracle Agent - Data Integrity Guard
                from services.agents.oracle_agent import oracle_agent
                await oracle_agent.initialize()
                await kernel.register_agent(oracle_agent)
                
                # 🆕 [V110.113] Threshold Calibrator - Auto-calibration
                from services.threshold_calibrator import threshold_calibrator
                await threshold_calibrator.initialize()
                if threshold_calibrator.enabled:
                    logger.info("📊 [V110.113] Threshold Calibrator ENABLED - Auto-calibration active")
                else:
                    logger.info("📊 [V110.113] Threshold Calibrator DISABLED - Using static thresholds")

                # 🆕 [V110.210] Flow Sentinel - Integrity Guard
                try:
                    from services.agents.flow_sentinel import flow_sentinel
                    await flow_sentinel.start()
                    await kernel.register_agent(flow_sentinel)
                except Exception as fe:
                    logger.error(f"❌ Falha ao carregar FlowSentinel: {fe}")

                await kernel.register_agent(captain_agent)
                await kernel.register_agent(fleet_audit)
                await kernel.register_agent(macro_analyst)
                await kernel.register_agent(whale_tracker)
                await kernel.register_agent(sentiment_specialist)
                await kernel.register_agent(librarian_agent)
                await kernel.register_agent(harvester_agent)
                logger.info("Step 3.0: [V110.240] AIOS Kernel — Fleet Active 🚀")

                # Start Core Loops
                asyncio.create_task(sig_gen._sync_radar_rtdb()) # [V15.7.6] Initial sync
                asyncio.create_task(sig_gen.monitor_and_generate())
                asyncio.create_task(sig_gen.track_outcomes())
                asyncio.create_task(sig_gen.radar_loop())
                asyncio.create_task(captain_agent.monitor_signals())
                asyncio.create_task(captain_agent.monitor_active_positions_loop())
                asyncio.create_task(librarian_agent.run_loop())
                

                
                # 🆕 [V110.113] Threshold Calibration Loop
                async def threshold_calibration_loop():
                    while True:
                        try:
                            await asyncio.sleep(3600)  # Checa a cada hora
                            if threshold_calibrator.should_calibrate():
                                logger.info("🔧 [V110.113] Running automatic threshold calibration...")
                                result = await threshold_calibrator.run_calibration()
                                if result.get("success"):
                                    logger.info(f"✅ [V110.113] Calibration complete: PF={result['profit_factor']:.2f}")
                                else:
                                    logger.warning(f"⚠️ [V110.113] Calibration skipped: {result.get('reason')}")
                        except Exception as e:
                            logger.error(f"❌ [THRESH-CAL] Error in calibration loop: {e}")
                
                asyncio.create_task(threshold_calibration_loop())
                
                # [V27.2] Trade Analyst - Performance Intelligence (KEPT)
                from services.agents.trade_analyst import trade_analyst
                await kernel.register_agent(trade_analyst)
                asyncio.create_task(trade_analyst.start_loop())
                
                # Position reaper ENABLED - handles ghost slot cleanup
                asyncio.create_task(bankroll_manager.position_reaper_loop())
                
                # 3.1: V5.2.3: Initial Sync - Ensure Vault and Banca are aligned with history
                async def initial_sync():
                    try:
                        from services.vault_service import vault_service
                        logger.info("Step 3.1: Running initial Vault & Banca Synchronization...")
                        await vault_service.sync_vault_with_history()
                        await bankroll_manager.update_banca_status()
                        
                        # [V110.25.1] Legacy startup cleanup removed to preserve slot persistence.
                        # BankrollManager now handles safe ghost-busting with 10m grace period.
                        logger.info("Step 3.1: Initial Sync COMPLETE ✅")
                    except Exception as e:
                        logger.error(f"Step 3.1: Initial Sync ERROR: {e}")
                
                asyncio.create_task(initial_sync())
                
                # 4. Start Paper Execution Engine (Simulator only)
                logger.info(f"[DEBUG INIT] settings.BYBIT_EXECUTION_MODE={settings.BYBIT_EXECUTION_MODE}")
                logger.info(f"[DEBUG INIT] bybit_rest_service.execution_mode={bybit_rest_service.execution_mode}")
                if bybit_rest_service.execution_mode == "PAPER":
                    logger.info("Step 4: Paper Execution Engine ACTIVATING...")
                    asyncio.create_task(bybit_rest_service.run_paper_execution_loop())
                else:
                    logger.info(f"Step 4: [V27.3] {bybit_rest_service.execution_mode} Execution Engine (Smart SL) ACTIVATING...")
                    asyncio.create_task(bybit_rest_service.run_real_execution_loop())

                # Sovereign Pulse Loop (WebSocket only)
                async def pulse_loop():
                    while True:
                        # [V110.175] Native Railway Heartbeat (Implemented in update_pulse_drag)
                        await asyncio.sleep(60)
                asyncio.create_task(pulse_loop())

                async def market_context_loop():
                    while True:
                        try:
                            if bybit_ws_service:
                                await bybit_ws_service.update_market_context()
                                
                                # 🆕 [V110.175] FEED THE ORACLE: Alimenta o oráculo com dados reais do WebSocket
                                if oracle_agent:
                                    await oracle_agent.update_market_data("bybit_ws", {
                                        "btc_price": bybit_ws_service.btc_price,
                                        "btc_adx": bybit_ws_service.btc_adx,
                                        "btc_variation_1h": bybit_ws_service.btc_variation_1h,
                                        "btc_variation_24h": bybit_ws_service.btc_variation_24h,
                                        "btc_variation_15m": bybit_ws_service.btc_variation_15m
                                    })

                                # Sync to RTDB for immediate UI update
                                if sig_gen:
                                    # 🆕 [V110.32.1] Fetch Validated Context from Oracle
                                    oracle_ctx = {}
                                    if oracle_agent:
                                        oracle_ctx = oracle_agent.get_validated_context()
                                        # Use Oracle ADX if available to ensure "Amnesia Guard" consistency in UI
                                        current_adx = oracle_ctx.get("btc_adx", getattr(bybit_ws_service, 'btc_adx', 20.0))
                                    else:
                                        current_adx = getattr(bybit_ws_service, 'btc_adx', 20.0)
                                    
                                    # Fallback final para evitar "..."
                                    if not current_adx or current_adx < 0.1:
                                        current_adx = 20.0

                                    # 🆕 [V110.33] Fetch BTC Dominance from Macro Analyst
                                    current_dominance = 0.0
                                    try:
                                        from services.agents.macro_analyst import macro_analyst
                                        current_dominance = await macro_analyst._get_btc_dominance()
                                        # Sync dominance to Oracle for LKG persistence
                                        if oracle_agent and current_dominance > 0:
                                            await oracle_agent.update_market_data("macro_analyst", {"dominance": current_dominance})
                                    except Exception as dom_err:
                                        logger.warning(f"Dominance fetch error: {dom_err}")

                                    # 🆕 [V110.34] Calculate Captain-Aligned Direction
                                    # MUST mirror captain.get_deep_macro_status() exactly:
                                    # ADX >= 30 + convergência 15m/1h = TRENDING, senão LATERAL
                                    btc_var_15m = getattr(bybit_ws_service, 'btc_variation_15m', 0.0)
                                    btc_var_1h = bybit_ws_service.btc_variation_1h
                                    if current_adx >= 30:
                                        if btc_var_15m > 0 and btc_var_1h > 0:
                                            captain_direction = "UP"
                                        elif btc_var_15m < 0 and btc_var_1h < 0:
                                            captain_direction = "DOWN"
                                        else:
                                            captain_direction = "LATERAL"
                                    else:
                                        captain_direction = "LATERAL"

                                    await sovereign_service.update_pulse_drag(
                                        btc_drag_mode=getattr(sig_gen, 'btc_drag_mode', False),
                                        btc_cvd=bybit_ws_service.get_cvd_score("BTCUSDT"),
                                        exhaustion=getattr(sig_gen, 'exhaustion_level', 0.0),
                                        btc_price=bybit_ws_service.btc_price,
                                        btc_var_1h=btc_var_1h,
                                        btc_adx=current_adx,
                                        decorrelation_avg=getattr(bybit_ws_service, 'decorrelation_avg', 0.0),
                                        btc_var_24h=bybit_ws_service.btc_variation_24h,
                                        btc_dominance=current_dominance,
                                        btc_var_15m=btc_var_15m,
                                        btc_direction=captain_direction,
                                        oracle_context=oracle_ctx
                                    )
                                    
                                    payload = {
                                        "btc_price": bybit_ws_service.btc_price,
                                        "btc_variation_1h": btc_var_1h,
                                        "btc_adx": current_adx,
                                        "btc_direction": captain_direction,
                                        "btc_dominance": current_dominance,
                                        "btc_var_15m": btc_var_15m,
                                        "timestamp": time.time()
                                    }
                                    # 🆕 [V110.181] BROADCAST SYSTEM STATE: Sincronização nativa WebSocket
                                    from services.websocket_service import websocket_service
                                    await websocket_service.emit_system_state(payload)

                        except Exception as e:
                            logger.error(f"Error in market_context_loop: {e}")
                        await asyncio.sleep(10) # 🆕 Optimized for V110.32.1 (from 300s)
                asyncio.create_task(market_context_loop())

                async def bankroll_loop():

                    while True:
                        try: await bankroll_manager.update_banca_status()
                        except: pass
                        await asyncio.sleep(60)
                asyncio.create_task(bankroll_loop())

                # 5. Start MCP Bridge for AIOS Integration (DISABLED - V27.3.1 - Fix startup crash)
                # try:
                #     from services.mcp_bridge import start_mcp_server
                #     asyncio.create_task(start_mcp_server())
                #     logger.info("Step 5: AIOS MCP Bridge SCHEDULED ✅")
                # except Exception as e:
                #     logger.warning(f"Step 5: MCP Bridge Load Error: {e}")

            except Exception as e:
                logger.error(f"Step 3: Agent sync error: {e}")
                
            logger.info("\u2705 All background services started successfully!")
        except Exception as e:
            logger.error(f"FATAL Startup Error: {e}", exc_info=True)
            
    # Start worker
    asyncio.create_task(start_services())
    
    yield
    
    # 🛑 [V110.176] CLEAN SHUTDOWN PROTOCOL
    logger.info("🛑 [V110.176] 10D Sniper Intelligence Lab - SHUTTING DOWN...")
    try:
        if bybit_ws_service:
            bybit_ws_service.stop()
        if redis_service:
            # redis_service has an async client but connect() doesn't expose a clean close yet, 
            # let's try a best effort if it has aclose
            if hasattr(redis_service.client, "aclose"):
                await redis_service.client.aclose()
    except Exception as shutdown_err:
        logger.error(f"Error during shutdown: {shutdown_err}")
    
    logger.info("🔚 End of Lifespan. Goodbye.")

app = FastAPI(
    title=f"1CRYPTEN SPACE {VERSION} API",
    version=VERSION,
    lifespan=lifespan
)

# Configure CORS - V15.1.5 Security Hardening
# In production, restrict this. For local dev/file open, * is risky but often used.
# Let's target the exact port 8085 as default.
ALLOWED_ORIGINS = [
    "http://localhost:8085",
    "http://127.0.0.1:8085",
    "http://localhost:5173",
    "https://1crypten.space",
    "https://www.1crypten.space",
    "https://10d50-production.up.railway.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(NoCacheMiddleware)

# [V1.0] Servir provas visuais do Agente Visão
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR, exist_ok=True)
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# =================================================================
# ROUTES & MODULARIZATION (V110.25.0)
# =================================================================
from routes import trading, system, dashboard, market, aios, chat, vault, backtest_routes, auth

# Include Modulated Routers
app.include_router(auth.router)
app.include_router(trading.router)
app.include_router(system.router)
app.include_router(dashboard.router)
app.include_router(market.router)
app.include_router(aios.router)
app.include_router(chat.router)
app.include_router(vault.router)
app.include_router(backtest_routes.router)

# =================================================================
# WEBSOCKET ENDPOINT (V110.175)
# =================================================================
from services.websocket_service import websocket_service
from fastapi import WebSocket, WebSocketDisconnect

@app.websocket("/ws/cockpit")
async def cockpit_websocket_endpoint(websocket: WebSocket):
    await websocket_service.connect(websocket)
    try:
        while True:
            # Mantém a conexão viva e aguarda mensagens (opcional)
            data = await websocket.receive_text()
            # Se receber um ping do front, podemos responder
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        websocket_service.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket Error: {e}")
        websocket_service.disconnect(websocket)

# Special Root Routes (Must stay in main for precedence or special handling)
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "cockpit.html"))

@app.get("/cockpit")
@app.get("/cockpit.html")
async def cockpit_redirect():
    return RedirectResponse(url="/")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    # Search for physical file first (crucial for manifest.json, sw.js, etc.)
    file_path = os.path.join(FRONTEND_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
        
    # SECURITY: Never catch-all API routes that DON'T correspond to files
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # SPA Fallback
    return FileResponse(os.path.join(FRONTEND_DIR, "cockpit.html"))

if __name__ == "__main__":
    target_port = settings.PORT
    target_host = settings.HOST
    logger.info(f"Server starting on http://{target_host}:{target_port}")
    uvicorn.run(app, host=target_host, port=target_port, reload=False)

logger.info("🔚 End of main.py file reached")

