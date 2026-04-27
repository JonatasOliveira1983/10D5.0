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

        # [V5.0] OBSERVATORY UPGRADE: Usa o layout salvo do TradingView do usuário.
        # O chart gXpimIZU já tem SMA branca (21), SMA amarela (100),
        # Pivot Points SuperTrend e Volume configurados.
        self.TV_CHART_ID = "gXpimIZU"
        self.tv_base_url = f"https://www.tradingview.com/chart/{self.TV_CHART_ID}/"

        # [V5.0] FALLBACK: Widget embed caso o layout salvo falhe
        self.fallback_url = (
            "https://s.tradingview.com/widgetembed/?"
            "symbol=BYBIT:{symbol}.P&"
            "interval={interval}&"
            "hidesidetoolbar=1&symboledit=0&saveimage=0&"
            "toolbarbg=111111&theme=dark&style=1&"
            "timezone=Etc%2FUTC&"
            "studies=%5B%7B%22id%22%3A%22MASimple%40tv-basicstudies%22%2C%22inputs%22%3A%7B%22length%22%3A21%7D%7D%2C%7B%22id%22%3A%22MASimple%40tv-basicstudies%22%2C%22inputs%22%3A%7B%22length%22%3A100%7D%7D%5D"
        )

    async def capture_chart(self, symbol: str, interval: str = "30") -> str:
        """
        [V5.0] Captures a screenshot using the user's saved TradingView layout.
        The layout already has SMA 21 (white), SMA 100 (yellow), SuperTrend Pivot and Volume.
        Falls back to widget embed if the layout URL fails.
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
        Opens the user's saved TradingView layout with the target symbol.
        This preserves all indicator settings (SMA, SuperTrend Pivot, Volume).
        """
        tv_symbol = f"BYBIT:{symbol}.P"
        url = f"{self.tv_base_url}?symbol={tv_symbol}"

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

                await page.goto(url, wait_until="domcontentloaded", timeout=60000)

                # [V5.0] Wait for TradingView chart canvas to be rendered
                try:
                    await page.wait_for_selector("canvas", timeout=20000)
                    await asyncio.sleep(6)  # Extra time for indicators to render
                except Exception:
                    await asyncio.sleep(10)  # Fallback wait

                await page.screenshot(path=filepath, full_page=False)
                await browser.close()

                logger.info(f"✅ [SCREENSHOT-V5] Saved layout screenshot: {filepath}")
                return filepath
        except Exception as e:
            logger.error(f"❌ [SCREENSHOT-V5] Saved layout error for {symbol}: {e}")
            return ""

    async def _capture_widget_embed(self, symbol: str, interval: str, filepath: str) -> str:
        """[V5.0] Fallback: captures the TradingView widget embed."""
        url = self.fallback_url.format(symbol=symbol, interval=interval)
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(viewport={'width': 1280, 'height': 720})
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(8)
                await page.screenshot(path=filepath)
                await browser.close()
                logger.info(f"✅ [SCREENSHOT-FALLBACK] Widget embed screenshot: {filepath}")
                return filepath
        except Exception as e:
            logger.error(f"❌ [SCREENSHOT-FALLBACK] Failed: {e}")
            return ""

screenshot_service = ScreenshotService()

