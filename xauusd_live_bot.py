"""
===============================================================================
Master Orchestrator & Live Bot Launcher
-------------------------------------------------------------------------------
Runs background polling, coordinates market scans, and dispatches alerts.
===============================================================================
"""

import asyncio
import logging
from market_data import MarketDataStreamer
from signal_engine import SignalEngine

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("XAUUSD_Bot")


async def main():
    logger.info("🚀 Booting XAUUSD Institutional Engine (v2 Super Upgrade)...")
    
    data_streamer = MarketDataStreamer(symbol="GC=F")
    engine = SignalEngine(account_balance=10.0, max_risk_pct=1.0)

    logger.info("📡 Scanning 5m, 15m, and 1h market structures...")

    # Fetch initial candle data
    df_5m = await data_streamer.fetch_ohlcv("5m")
    df_15m = await data_streamer.fetch_ohlcv("15m")
    df_1h = await data_streamer.fetch_ohlcv("1h")

    if not df_15m.empty:
        signal_output = engine.process_market_scan(df_5m, df_15m, df_1h, target_tf="15m")
        if signal_output:
            print("\n" + signal_output + "\n")

    # Main continuous monitoring loop (Runs every 5 seconds)
    logger.info("🟢 Bot Active — Monitoring price & 5-minute Auto-Drop TTL...")
    while True:
        try:
            current_price = await data_streamer.get_current_tick()
            if current_price > 0:
                drops = engine.evaluate_auto_drops(current_price)
                for drop_alert in drops:
                    logger.warning(drop_alert)

            await asyncio.sleep(5)
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user.")
            break
        except Exception as e:
            logger.error(f"Execution Error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
