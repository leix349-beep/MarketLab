# MarketLab

**An explainable equity-research platform built by Xiang as a student research project.**

MarketLab brings mathematics, financial research, and reproducible experimentation into one bilingual web application. It is designed to test hypotheses, compare assets and strategies, study risk, and preserve research evidence—not to recommend securities or place orders.

> **Research question:** Can explainable technical and sector signals improve risk-adjusted performance in U.S. equities when evaluated without look-ahead bias?

## Research modules

- **Stock Research** — candlesticks, volume, technical indicators, backtesting, trade logs, parameter experiments, and daily reports
- **Sector Research** — relative strength, return, and volatility comparisons across 11 standard U.S. sector ETFs
- **Comparison Lab** — normalized performance, drawdown, rolling volatility, and correlation for up to four assets
- **Strategy Lab** — fair comparison of buy-and-hold, trend, mean-reversion, breakout, and trend-plus-RSI strategies
- **Regression Lab** — OLS market model, Beta, annualized Alpha, R², residual analysis, rolling Beta, and bootstrap confidence intervals

## Research design

- Indicators use only information available at the time; signals execute at the next trading day's open.
- Strategies are compared over identical date ranges with consistent fee and slippage assumptions.
- Formal runs can preserve parameters, retrieval timestamps, results, and reproducibility information.
- Positive, negative, and failed experiments are retained to reduce result-selection bias.
- Historical backtests are clearly separated from unfinished out-of-sample validation.

## Mathematics in the project

The current prototype connects market data to concepts including return and volatility, covariance and correlation, Alpha and Beta, the Sharpe and Sortino ratios, ordinary least-squares regression, residuals, rolling estimates, and bootstrap confidence intervals.

Planned mathematical extensions include parameter-stability surfaces, walk-forward validation, Monte Carlo simulation, portfolio optimization, principal component analysis, and market-regime models.

## Reproducibility and data records

Local research runs are organized under `research_records/`:

- `raw_data/` — timestamped market-data snapshots
- `experiment_manifests/` — parameters and reproducibility metadata
- `parameter_experiments/` — parameter and mathematical experiment outputs
- `sector_snapshots/` — sector-research snapshots
- `daily_reports/` — generated daily research reports
- `experiments.csv` — local experiment index

Generated research records remain local by default. The public repository contains source code, methodology, validation notes, and reviewed non-private examples only.

## Run locally on Windows

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Open `http://localhost:8501`. The interface supports English and Chinese.

## Current limitations

- Free market-data sources can be delayed, revised, or temporarily unavailable.
- Strategies still require walk-forward out-of-sample validation and stronger statistical testing.
- Results may be affected by parameter selection, survivorship bias, and changing market regimes.
- Alpha, Beta, and correlation describe historical relationships; they do not establish causality.
- All outputs are historical research results and are not investment advice.

## Roadmap

The next research milestones are:

1. Walk-forward validation and parameter-stability heatmaps
2. Portfolio construction, efficient frontiers, and Monte Carlo experiments
3. Timestamped and source-cited news event studies
4. Weekly reports, a research paper, a poster, and a public results page

See [`ROADMAP.md`](ROADMAP.md) for the complete research plan and [`DEPLOYMENT.md`](DEPLOYMENT.md) for the public-test checklist.

## Security

The repository excludes virtual environments, caches, generated research records, and credential files. Never commit `.env`, `.streamlit/secrets.toml`, API keys, brokerage credentials, or account information.

<details>
<summary><strong>中文简介</strong></summary>

### 项目定位

MarketLab 是 Xiang 构建的双语学生研究项目，将数学、金融研究和可复现实验整合到一个网站中。它用于提出假设、回测策略、比较资产、研究风险并保存研究证据，不用于荐股，也不会提交真实或模拟订单。

### 核心研究问题

在避免前视偏差、统一交易成本并进行样本外检验时，可解释的技术与板块信号能否改善美股策略的风险调整后表现？

### 当前模块

- **股票研究**：K线、成交量、技术指标、回测、交易记录、参数实验与每日研究报告
- **板块研究**：11个标准美国行业ETF的相对强弱、收益与波动率比较
- **资产比较**：最多四个资产的标准化表现、回撤、滚动波动率与相关矩阵
- **策略实验室**：在相同数据和成本假设下比较长期持有、趋势、均值回归、突破与趋势加RSI策略
- **回归实验室**：OLS市场模型、Beta、年化Alpha、R²、残差、滚动Beta与bootstrap置信区间

### 研究原则

- 指标只使用当时已经存在的信息，信号在下一交易日开盘执行。
- 所有策略使用相同的数据区间、费用与滑点假设。
- 正面、负面和失败实验都会保留，避免只展示最好看的结果。
- 当前结果仍属于历史回测，不构成投资建议。

</details>

## Copyright

Copyright © 2026 Xiang. All rights reserved.

This repository is published for educational review and portfolio demonstration. No permission is granted to reproduce, redistribute, or create derivative works without written authorization.

本项目仅用于教育评审、研究展示与个人作品集展示。未经作者书面许可，不得复制、重新分发或创作衍生作品。
