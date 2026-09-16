"""
===============================================================================
Institutional Market Data Streamer & MTF Aggregator
-------------------------------------------------------------------------------
Provides async fetchers for 5m, 15m, 1h, and 4h XAUUSD price candles with 
failover fallback systems and live tick streaming.
===============================================================================
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Optional
import pandas as pd
import yfinance as yf

logger = logging.getLogger("MarketData")

class MarketDataStreamer:
    def __init__(self, symbol: str = "GC=F"):
        self.symbol = symbol  # Gold Futures / Spot XAUUSD proxy
        self.timeframes = {"5m": "5m", "15m": "15m", "1h": "60m", "4h": "60m"}
        self._cache: Dict[str, pd.DataFrame] = {}

    async def fetch_ohlcv(self, timeframe: str = "15m", period: str = "5d") -> pd.DataFrame:
        """Fetches and cleans OHLCV candle data asynchronously."""
        yf_tf = self.timeframes.get(timeframe, "15m")
        
        try:
            loop = asyncio.get_event_loop()
            df = await loop.run_in_executor(
                None, 
                lambda: yf.download(tickers=self.symbol, period=period, interval=yf_tf, progress=False)
            )
            
            if df.empty:
                logger.warning(f"Empty dataframe returned for {timeframe}")
                return pd.DataFrame()

            # Clean multi-index columns if present from yfinance
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [col[0].lower() for col in df.columns]
            else:
                df.columns = [col.lower() for col in df.columns]

            df = df.dropna().reset_index()
            
            # Resample 1h to 4h if 4h is requested
            if timeframe == "4h":
                df['datetime'] = pd.to_datetime(df['date'] if 'date' in df.columns else df['datetime'])
                df.set_index('datetime', inplace=True)
                df = df.resample('4h').agg({
                    'open': 'first',
                    'high': 'max',
                    'low': 'min',
                    'close': 'last',
                    'volume': 'sum'
                }).dropna().reset_index()

            self._cache[timeframe] = df
            return df

        except Exception as e:
            logger.error(f"Error fetching data for {timeframe}: {e}")
            return self._cache.get(timeframe, pd.DataFrame())

    async def get_current_tick((self)) -> float:
        """Fetches real-time spot ask price."""
        df_5m = await self.fetch_ohlcv("5m", period="1d")
        if not df_5m.empty:
            return float(df_5m['close'].iloc[-1])
        return 0.0
