import os
import asyncio
import logging
import time
from playwright.async_api import async_playwright

logger = logging.getLogger("ScreenshotService")

class ScreenshotService:
    def __init__(self):
        # [V4.3] FIXED PATHING: Use file-relative paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "assets", "vision_proofs")

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

        # [V5.0] PROPRIETARY ENGINE: Captura o Observatório local/produção
        self.observatory_url = "https://1crypten.space/observatory"
        
    async def capture_chart(self, symbol: str, interval: str = "30") -> str:
        """
        [V5.0] Captura o gráfico usando o Motor Proprietário (Lightweight Charts).
        O Observatório já calcula SMA 21, SMA 100 e SuperTrend localmente.
        Returns the absolute path to the saved image.
        """
        symbol = symbol.replace(".P", "").upper()
        filename = f"vision_{symbol}_{interval}_{int(time.time())}.png"
        filepath = os.path.join(self.output_dir, filename)

        logger.info(f"📸 [SCREENSHOT-V5] Capturing chart for {symbol} ({interval}m) via saved layout...")

        try:
            result = await self._capture_saved_layout(symbol, filepath)
            if result:
                return result
            # Fallback to widget embed
            logger.warning(f"⚠️ [SCREENSHOT] Saved layout capture failed for {symbol}. Falling back to widget embed.")
            return await self._capture_widget_embed(symbol, interval, filepath)
        except Exception as e:
            logger.error(f"❌ [SCREENSHOT-ERROR] Failed to capture chart for {symbol}: {e}")
            return ""

    async def _capture_saved_layout(self, symbol: str, filepath: str) -> str:
        """
        [V5.0] Abre o Observatório proprietário para capturar o gráfico com indicadores.
        """
        url = f"{self.observatory_url}?symbol={symbol}&s={symbol}"

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
                )
                context = await browser.new_context(
                    viewport={'width': 1440, 'height': 900},
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Navega para o Observatório
                await page.goto(url, wait_until="networkidle", timeout=60000)

                # Aguarda o motor de gráfico renderizar (procura pelo canvas do Lightweight Charts)
                try:
                    await page.wait_for_selector("canvas", timeout=30000)
                    await asyncio.sleep(5) # Tempo para os indicadores calcularem
                except Exception:
                    await asyncio.sleep(10)

                # Captura a visão do Observatório
                await page.screenshot(path=filepath)
                await browser.close()

                logger.info(f"✅ [SCREENSHOT-V5] Observatory Proprietary screenshot: {filepath}")
                return filepath
        except Exception as e:
            logger.error(f"❌ [SCREENSHOT-V5] Observatory capture error for {symbol}: {e}")
            return ""

    async def _capture_widget_embed(self, symbol: str, interval: str, filepath: str) -> str:
        # Fallback removido: agora usamos apenas o motor proprietário
        return await self._capture_saved_layout(symbol, filepath)

screenshot_service = ScreenshotService()

