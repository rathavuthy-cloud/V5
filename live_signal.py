"""
===============================================================================
Institutional Raw Signal Formatter
-------------------------------------------------------------------------------
Generates high-converting, professional Telegram alert templates.
===============================================================================
"""

class LiveSignalFormatter:
    @staticmethod
    def format_signal(
        timeframe: str,
        direction: str,
        entry: float,
        stop_loss: float,
        tp1: float,
        tp2: float,
        confluence_score: int,
        confidence: str,
        wins: int = 0,
        losses: int = 4,
        open_trades: int = 3,
        balance: float = 10.0,
        risk_pct: float = 1.0
    ) -> str:
        sl_pips = abs(entry - stop_loss)
        rr = round(abs(tp1 - entry) / sl_pips, 1) if sl_pips > 0 else 2.0
        
        # Risk Calculation for Standard Lots (0.01 lot = $10 per point on 100oz XAUUSD)
        risk_usd = round(sl_pips * 10.0, 2)
        risk_percent = round((risk_usd / balance) * 100, 1)
        
        time_label = "Next 5 min" if timeframe == "5m" else f"Next {timeframe}"

        # Risk Warning Guard for Small Balances ($10.00 base)
        warning_msg = ""
        if risk_usd > (balance * (risk_pct / 100.0)):
            warning_msg = (
                f"\n⚠️ Too small to size safely at ${balance:.1f} balance / {risk_pct:.1f}% risk "
                f"and a {sl_pips:.2f} stop — even the smallest tradeable size (0.01 lot) would risk "
                f"${risk_usd:.2f} ({risk_percent:.1f}% of your account). Options: use /contractsize if your "
                f"broker offers smaller XAUUSD contracts, trade a cent account, or grow the account "
                f"before sizing into gold at standard lots."
            )

        total_trades = wins + losses
        win_rate = int((wins / total_trades) * 100) if total_trades > 0 else 0
        icon = "🔴" if direction.upper() == "SELL" else "🟢"

        return f"""⚠️ Auto-signals active — Multi-Timeframe Engine ({timeframe.upper()})
🏆 XAUUSD PREMIUM SIGNAL
Scanner confluence: {confluence_score}/4 factors aligned · {confidence} confidence
──────────────────
Signal: {direction.upper()}
Entry: {entry:.2f}
Stop Loss: {stop_loss:.2f}
Take Profit 1: {tp1:.2f}
Take Profit 2: {tp2:.2f}
Confidence: {confidence}
Risk:Reward: 1:{rr}
Timeframe: ⚡ {time_label}
──────────────────
📍 Entry {entry:.2f}
🛑 Stop {stop_loss:.2f}
🎯 TP1 {tp1:.2f}
🎯 TP2 {tp2:.2f}
🛡️ R:R 1:{rr} · ⏳ Hold ⚡ {time_label}
──────────────────
{icon} ⏰ Entry trigger · {direction.upper()} on retest of {entry:.2f} (zone {entry - 0.55:.2f}–{entry + 0.55:.2f})
Valid for next ~{timeframe} · Active Session Volume ⚡
If price moves through the zone without filling — setup expired, don't chase.
──────────────────
📈 Track record: {wins}W/{losses}L ({win_rate}%) · {open_trades} open
⚠️ Automated technical analysis — not financial advice. Never risk more than you can afford to lose.{warning_msg}"""
