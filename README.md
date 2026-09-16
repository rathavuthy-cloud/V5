# XAUUSD Institutional Multi-Timeframe Bot (V2 Upgrade)

Advanced XAUUSD / Gold automated signal generator and risk management system built on Smart Money Concepts (SMC) and ICT principles.

## Core Features
* **Multi-Timeframe Scanning**: Analyzes 5m, 15m, 1h, and 4h structural shifts.
* **ICT / SMC Indicators**: Fair Value Gaps (FVG) with 50% Consequent Encroachment (CE), Order Blocks, and Liquidity Sweeps (PDH/PDL).
* **5-Minute Auto-Drop Engine**: Drops expired unfilled signals automatically after 5 minutes or upon structural invalidation.
* **Small Account Protection**: Built-in risk calculator optimized for micro accounts ($10 base balance).
* **Cloud Deployment Ready**: Configured with `Procfile` for 24/7 background worker execution on Heroku/Railway/Render.

## How to Deploy
1. Clone repository:
   ```bash
   git clone [https://github.com/rathavuthy-cloud/v2.git](https://github.com/rathavuthy-cloud/v2.git)
   cd v2
