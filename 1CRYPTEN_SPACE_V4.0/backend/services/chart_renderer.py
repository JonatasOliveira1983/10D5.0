import os
import time
import pandas as pd
import mplfinance as mpf
import logging
from typing import List, Dict, Any

logger = logging.getLogger("ChartRenderer")

class ChartRenderer:
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_dir, "assets", "vision_proofs")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def render_chart(self, symbol: str, df: pd.DataFrame, obs: List[Dict] = None, fvgs: List[Dict] = None) -> str:
        """
        [V5.0 PURE PYTHON] Renders a professional chart image with SMC overlays.
        """
        try:
            symbol = symbol.replace(".P", "").upper()
            filename = f"pure_vision_{symbol}_{int(time.time())}.png"
            filepath = os.path.join(self.output_dir, filename)

            # 1. Prepare Data
            df = df.copy()
            df.index = pd.to_datetime(df.index)
            
            # 2. Indicators
            df['sma21'] = df['close'].rolling(window=21).mean()
            df['sma100'] = df['close'].rolling(window=100).mean()

            # 3. SuperTrend (Simplified for V1)
            # We can use a basic version or just skip for now to ensure stability
            
            # 4. Styling
            mc = mpf.make_marketcolors(up='#00ff9d', down='#ff3b3b',
                                      edge='inherit', wick='inherit',
                                      volume='in', ohlc='inherit')
            
            s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc, 
                                  gridstyle='', facecolor='#0d0d0d', 
                                  edgecolor='#262626', figcolor='#0d0d0d')

            # 5. Overlays (SMA)
            apds = [
                mpf.make_addplot(df['sma21'], color='#ffffff', width=1.0),
                mpf.make_addplot(df['sma100'], color='#ffcc00', width=1.0)
            ]

            # 6. SMC Annotations (OBs)
            # For OBs, we will draw horizontal lines or boxes using mpf.make_addplot or hlines
            hlines_list = []
            hlines_colors = []
            
            if obs:
                for ob in obs[-3:]: # Only show last 3 OBs to avoid clutter
                    color = '#00ff9d44' if ob['type'] == 'BULLISH' else '#ff3b3b44'
                    # We use hlines for the top and bottom of the OB
                    hlines_list.append(ob['top'])
                    hlines_colors.append(color)
                    hlines_list.append(ob['bottom'])
                    hlines_colors.append(color)

            # 7. Rendering
            # We use a smaller window of data for the final image (e.g. last 100 candles)
            plot_df = df.tail(100) if len(df) > 100 else df

            mpf.plot(plot_df, type='candle', style=s, 
                     addplot=apds if apds else None,
                     hlines=dict(hlines=hlines_list, colors=hlines_colors, linestyle='solid') if hlines_list else None,
                     volume=True, title=f"1CRYPTEN ELITE: {symbol}",
                     savefig=filepath, tight_layout=True,
                     datetime_format='%H:%M', xrotation=0)

            logger.info(f"🎨 [RENDERER] Pure Python Chart generated: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ [RENDERER] Failed to render chart for {symbol}: {e}")
            return ""

chart_renderer = ChartRenderer()
