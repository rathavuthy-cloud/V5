"""
===============================================================================
ICT / SMC Institutional Indicator Engine
-------------------------------------------------------------------------------
Calculates Fair Value Gaps (FVG), Consequent Encroachment (CE), Order Blocks,
Liquidity Sweeps (PDH/PDL), Market Structure Shifts (MSS), and Killzones.
===============================================================================
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional
import pandas as pd


@dataclass
class FairValueGap:
    timeframe: str
    top: float
    bottom: float
    consequent_encroachment: float  # 50% midpoint level
    fvg_type: str                  # "BULLISH_FVG" or "BEARISH_FVG"


@dataclass
class OrderBlock:
    timeframe: str
    high: float
    low: float
    ob_type: str                   # "BULLISH_OB" or "BEARISH_OB"


class SMCIndicators:
    @staticmethod
    def get_session_killzone(utc_now: datetime) -> str:
        """Determines active high-volume trading windows."""
        hour = utc_now.hour
        if 0 <= hour < 6:
            return "ASIA_SESSION"
        elif 7 <= hour < 10:
            return "LONDON_KILLZONE"
        elif 13 <= hour < 16:
            return "NY_KILLZONE"
        return "OFF_HOURS"

    @staticmethod
    def find_fvg(df: pd.DataFrame, timeframe: str) -> Optional[FairValueGap]:
        """Detects 3-candle imbalance (Fair Value Gap) with 50% CE level."""
        if len(df) < 4:
            return None

        # Analyze last completed candle pattern
        i = len(df) - 2
        c1_high, c1_low = df.loc[i - 1, 'high'], df.loc[i - 1, 'low']
        c3_high, c3_low = df.loc[i + 1, 'high'], df.loc[i + 1, 'low']

        # Bullish FVG (Gap between C1 High and C3 Low)
        if c3_low > c1_high:
            ce = c1_high + ((c3_low - c1_high) * 0.5)
            return FairValueGap(timeframe, c3_low, c1_high, ce, "BULLISH_FVG")

        # Bearish FVG (Gap between C1 Low and C3 High)
        if c3_high < c1_low:
            ce = c3_high + ((c1_low - c3_high) * 0.5)
            return FairValueGap(timeframe, c1_low, c3_high, ce, "BEARISH_FVG")

        return None

    @staticmethod
    def find_order_block(df: pd.DataFrame, timeframe: str, direction: str) -> Optional[OrderBlock]:
        """Identifies institutional order blocks before structural displacement."""
        if len(df) < 6:
            return None

        recent = df.tail(10).reset_index(drop=True)
        for idx in range(len(recent) - 3, 0, -1):
            candle = recent.iloc[idx]
            next_candle = recent.iloc[idx + 1]

            if direction == "BUY" and candle['close'] < candle['open'] and next_candle['close'] > candle['high']:
                return OrderBlock(timeframe, candle['high'], candle['low'], "BULLISH_OB")
            elif direction == "SELL" and candle['close'] > candle['open'] and next_candle['close'] < candle['low']:
                return OrderBlock(timeframe, candle['high'], candle['low'], "BEARISH_OB")

        return None

    @staticmethod
    def detect_liquidity_sweeps(df_1h: pd.DataFrame, df_lower: pd.DataFrame) -> Dict[str, bool]:
        """Scans for key liquidity sweeps above/below 24-hour extremes."""
        if len(df_1h) < 24:
            return {"swept_pdh": False, "swept_pdl": False}

        pdh = df_1h.tail(24)['high'].max()
        pdl = df_1h.tail(24)['low'].min()
        last_candle = df_lower.iloc[-1]

        return {
            "swept_pdh": last_candle['high'] > pdh and last_candle['close'] < pdh,
            "swept_pdl": last_candle['low'] < pdl and last_candle['close'] > pdl
        }
