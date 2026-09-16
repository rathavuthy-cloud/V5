"""
===============================================================================
Super-Thinking Multi-Timeframe Scoring & Auto-Drop Engine
-------------------------------------------------------------------------------
Evaluates 5m/15m/1h market conditions, ranks setups, and triggers 5m TTL drops.
===============================================================================
"""

import asyncio
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import pandas as pd

from indicators import SMCIndicators
from live_signal import LiveSignalFormatter


class SignalEngine:
    def __init__(self, account_balance: float = 10.0, max_risk_pct: float = 1.0):
        self.balance = account_balance
        self.max_risk_pct = max_risk_pct
        self.active_signals: Dict[str, Dict] = {}
        self.track_record = {"wins": 0, "losses": 4, "open": 0}

    def process_market_scan(
        self,
        df_5m: pd.DataFrame,
        df_15m: pd.DataFrame,
        df_1h: pd.DataFrame,
        target_tf: str = "15m"
    ) -> Optional[str]:
        """Performs multi-timeframe analysis and generates institutional signals."""
        utc_now = datetime.now(timezone.utc)
        killzone = SMCIndicators.get_session_killzone(utc_now)

        tf_map = {"5m": df_5m, "15m": df_15m, "1h": df_1h}
        df = tf_map.get(target_tf, df_15m)

        fvg = SMCIndicators.find_fvg(df, target_tf)
        if not fvg:
            return None

        direction = "BUY" if fvg.fvg_type == "BULLISH_FVG" else "SELL"
        ob = SMCIndicators.find_order_block(df, target_tf, direction)
        sweeps = SMCIndicators.detect_liquidity_sweeps(df_1h, df_5m)

        # High-Thinking Multi-Factor Scoring (0 to 4)
        confluence_score = 0
        if killzone != "OFF_HOURS":
            confluence_score += 1
        if (direction == "BUY" and sweeps["swept_pdl"]) or (direction == "SELL" and sweeps["swept_pdh"]):
            confluence_score += 1
        if fvg is not None:
            confluence_score += 1
        if ob is not None:
            confluence_score += 1

        # Reject low-probability trades
        if confluence_score < 2:
            return None

        confidence = "High" if confluence_score >= 4 else ("Medium" if confluence_score == 3 else "Low")
        
        entry = fvg.consequent_encroachment
        if direction == "BUY":
            sl = ob.low - 1.20 if ob else entry - 18.50
            tp1 = entry + abs(entry - sl) * 2.0
            tp2 = entry + abs(entry - sl) * 3.5
        else:
            sl = ob.high + 1.20 if ob else entry + 18.50
            tp1 = entry - abs(entry - sl) * 2.0
            tp2 = entry - abs(entry - sl) * 3.5

        # Time-To-Live (5m for 5m scalps, 15m for intraday)
        ttl_minutes = 5 if target_tf == "5m" else 15
        expiry = utc_now + timedelta(minutes=ttl_minutes)

        sig_id = f"XAU-{target_tf.upper()}-{int(utc_now.timestamp())}"
        self.active_signals[sig_id] = {
            "id": sig_id,
            "timeframe": target_tf,
            "direction": direction,
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "expiry": expiry
        }
        self.track_record["open"] = len(self.active_signals)

        return LiveSignalFormatter.format_signal(
            timeframe=target_tf,
            direction=direction,
            entry=entry,
            stop_loss=sl,
            tp1=tp1,
            tp2=tp2,
            confluence_score=confluence_score,
            confidence=confidence,
            wins=self.track_record["wins"],
            losses=self.track_record["losses"],
            open_trades=self.track_record["open"],
            balance=self.balance,
            risk_pct=self.max_risk_pct
        )

    def evaluate_auto_drops(self, current_price: float) -> List[str]:
        """Automatically drops expired or price-invalidated setups."""
        now = datetime.now(timezone.utc)
        dropped_alerts = []

        for sig_id, sig in list(self.active_signals.items()):
            reason = None
            
            # Expiration Check
            if now >= sig["expiry"]:
                reason = f"⏰ 5-Minute TTL Expired ({sig['timeframe']})"
            # Invalidation Check
            elif sig["direction"] == "BUY" and current_price <= sig["sl"]:
                reason = "🔴 Price breached Stop Loss before entry"
            elif sig["direction"] == "SELL" and current_price >= sig["sl"]:
                reason = "🔴 Price breached Stop Loss before entry"

            if reason:
                del self.active_signals[sig_id]
                dropped_alerts.append(f"❌ [AUTO-DROP] Signal `{sig_id}` dropped: {reason}")

        self.track_record["open"] = len(self.active_signals)
        return dropped_alertss
