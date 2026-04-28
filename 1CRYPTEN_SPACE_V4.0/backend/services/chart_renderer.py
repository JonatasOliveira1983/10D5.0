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

    def render_chart(self, symbol: str, df: pd.DataFrame, obs: List[Dict] = None, fvgs: List[Dict] = None, pattern_123: Dict = None) -> str:
        """
        [V5.6] Renders a professional chart image with SMC and 1-2-3 Strategy overlays.
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

            # 3. Styling
            mc = mpf.make_marketcolors(up='#00ff9d', down='#ff3b3b',
                                      edge='inherit', wick='inherit',
                                      volume='in', ohlc='inherit')
            
            s = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=mc, 
                                  gridstyle='', facecolor='#0d0d0d', 
                                  edgecolor='#262626', figcolor='#0d0d0d')

            # 4. Overlays (SMA)
            apds = []
            if not df['sma21'].dropna().empty:
                apds.append(mpf.make_addplot(df['sma21'], color='#ffffff', width=1.0))
            if not df['sma100'].dropna().empty:
                apds.append(mpf.make_addplot(df['sma100'], color='#ffcc00', width=1.0))

            # 5. SMC Annotations (OBs)
            hlines_list = []
            hlines_colors = []
            hlines_styles = []
            
            if obs:
                for ob in obs[-3:]:
                    color = '#00ff9d44' if ob['type'] == 'BULLISH' else '#ff3b3b44'
                    hlines_list.extend([ob['top'], ob['bottom']])
                    hlines_colors.extend([color, color])
                    hlines_styles.extend(['solid', 'solid'])

            # 6. [V5.6] 1-2-3 Pattern Annotations
            if pattern_123 and pattern_123.get('detected'):
                points = pattern_123.get('points', {})
                trigger_price = pattern_123.get('trigger_price')
                side = pattern_123.get('side', 'buy')
                
                # Markers for points 1, 2, 3
                # We use scatter plots on a dummy series
                for label, data in points.items():
                    marker_val = [float('nan')] * len(df)
                    # Use index if available, or try to find by timestamp if we had it
                    idx = data.get('idx')
                    if idx is not None and idx < len(df):
                        # Adjust price slightly for visibility
                        price = data.get('price')
                        offset = (df['high'].max() - df['low'].min()) * 0.05
                        display_price = price - offset if side == 'buy' else price + offset
                        marker_val[idx] = display_price
                        
                        marker_color = '#00ff9d' if side == 'buy' else '#ff3b3b'
                        apds.append(mpf.make_addplot(marker_val, type='scatter', markersize=100, 
                                                   marker=f'${label}$', color=marker_color))

                # Trigger Line
                if trigger_price:
                    hlines_list.append(trigger_price)
                    hlines_colors.append('#ffffff88')
                    hlines_styles.append('dashed')

            # 7. Rendering
            plot_df = df.tail(100) if len(df) > 100 else df
            
            # Filter hlines to only those within plot range (optional but good for stability)
            
            plot_kwargs = {
                'type': 'candle',
                'style': s,
                'volume': True,
                'title': f"1CRYPTEN ELITE: {symbol}",
                'tight_layout': True,
                'savefig': filepath,
                'datetime_format': '%H:%M',
                'xrotation': 0
            }
            if apds:
                plot_kwargs['addplot'] = apds
            if hlines_list:
                plot_kwargs['hlines'] = dict(hlines=hlines_list, colors=hlines_colors, linestyle=hlines_styles)

            mpf.plot(plot_df, **plot_kwargs)

            logger.info(f"🎨 [RENDERER] 1-2-3 Chart generated for {symbol}: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ [RENDERER] Failed to render chart for {symbol}: {e}")
            return ""

chart_renderer = ChartRenderer()
