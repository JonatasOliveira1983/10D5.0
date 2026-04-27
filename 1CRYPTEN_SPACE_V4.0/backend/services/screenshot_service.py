import os
import asyncio
import logging
import time
from playwright.async_api import async_playwright

logger = logging.getLogger("ScreenshotService")

class ScreenshotService:
    def __init__(self):
        self.output_dir = os.path.join(os.getcwd(), "1CRYPTEN_SPACE_V4.0", "backend", "assets", "vision_proofs")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        
        # Base URL for the chart widget (TradingView Embed)
        # Includes SMA 21 and 100 as requested by the user
        self.base_url = (
            "https://tradingview.com/widgetembed/?"
            "symbol=BYBIT:{symbol}.P&"
            "interval={interval}&"
            "hidesidetoolbar=1&"
            "symboledit=0&"
            "saveimage=0&"
            "toolbarbg=111111&"
            "theme=dark&"
            "style=1&"
            "timezone=Etc%2FUTC&"
            "studies=SMA@tv-basicstudies%20%7B%22length%22%3A21%7D%2CSMA@tv-basicstudies%20%7B%22length%22%3A100%7D"
        )

    async def capture_chart(self, symbol: str, interval: str = "30") -> str:
        """
        Captures a screenshot of the chart for a given symbol and interval.
        Returns the absolute path to the saved image.
        """
        symbol = symbol.replace(".P", "").upper()
        # Ensure correct symbol format for the widget
        target_symbol = f"{symbol}"
        
        url = self.base_url.format(symbol=target_symbol, interval=interval)
        filename = f"vision_{symbol}_{interval}_{int(time.time())}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        logger.info(f"📸 [SCREENSHOT] Capturing chart for {symbol} ({interval}m)...")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Create a context with a standard desktop viewport
                context = await browser.new_context(viewport={'width': 1280, 'height': 720})
                page = await context.new_page()
                
                # Navigate to the chart
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                # Wait for the chart to render indicators (approx 5s)
                await asyncio.sleep(5)
                
                # Take the screenshot
                await page.screenshot(path=filepath)
                
                await browser.close()
                logger.info(f"✅ [SCREENSHOT] Saved: {filepath}")
                return filepath
        except Exception as e:
            logger.error(f"❌ [SCREENSHOT-ERROR] Failed to capture chart for {symbol}: {e}")
            return ""

screenshot_service = ScreenshotService()
