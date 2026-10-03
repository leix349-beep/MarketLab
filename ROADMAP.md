# MarketLab Research & Product Roadmap

MarketLab is a bilingual, explainable student research platform for studying U.S. equities. Its goal is not to promise profitable predictions, but to produce reproducible experiments, honest evidence, and progressively stronger mathematical analysis.

## Progress legend

- `[x]` available in the current prototype
- `[~]` started but not yet research-grade
- `[ ]` planned

## 1. Research foundation

- [x] Bilingual English/Chinese interface
- [x] Historical market data
- [x] Adjustable moving-average, RSI, stop-loss, take-profit, fee and slippage parameters
- [x] Basic backtest and trade log
- [x] Buy-and-hold comparison
- [x] Sharpe ratio and maximum drawdown
- [x] Automatic experiment CSV archive
- [~] Reproducible daily research report
- [ ] Dataset version, model version and code version in every experiment
- [ ] Hypothesis, observation, failure reason and next-step fields
- [ ] Exportable experiment package
- [~] Persistent raw-data snapshots with source and retrieval timestamp
- [ ] SQLite experiment catalog linking data, parameters, model version and outputs
- [~] Reproducibility manifest and checksums for important experiments
- [ ] Data retention, backup and privacy policy

## 2. Sector & theme research

- [~] Basic comparison with SPY and representative sector ETF
- [ ] Complete GICS-style sector mapping
- [ ] Sector ETF dashboard and relative-strength ranking
- [ ] Sector momentum and rotation visualization
- [ ] Stock return decomposition: market, sector and company-specific components
- [~] Correlation matrix across sectors and stocks
- [ ] Custom research themes: AI, semiconductors, cloud, EV, cybersecurity and others
- [ ] Theme definitions, membership history and survivorship-bias notes

Completion standard: answer whether a stock move is explained by the broad market, its sector, or stock-specific information.

## 1A. Visual design system & interaction

- [ ] Consistent bilingual typography, spacing, color and chart tokens
- [ ] Research-focused light and dark themes
- [ ] Subtle gradient accents for navigation and key research states
- [ ] Smooth section reveal and restrained scroll transitions
- [ ] Sticky research controls and clear active-section navigation
- [ ] Responsive desktop, tablet and mobile layouts
- [ ] Loading, empty, success, warning and data-quality states
- [ ] Reduced-motion accessibility preference
- [ ] Visual hierarchy that separates evidence, interpretation and controls

Completion standard: the interface feels polished and calm without animation obscuring data, slowing analysis or implying certainty.

## 3. Strategy laboratory

- [x] Moving-average trend strategy
- [x] RSI filter
- [x] Mean-reversion strategy
- [ ] Momentum strategy
- [x] Breakout strategy
- [ ] Bollinger Band strategy
- [ ] Multi-signal score strategy
- [ ] Sector-regime filter
- [ ] News-sentiment filter
- [~] Strategy comparison table with identical data and cost assumptions
- [ ] Explainable decision trace for every trade

Completion standard: compare strategies fairly against each other and against passive benchmarks.

## 4. Mathematics laboratory

- [x] Annualized return and volatility
- [x] Alpha, Beta and Sortino ratio
- [x] Return distribution and monthly return heatmap
- [~] Plain-language bilingual mathematical explanations
- [ ] Covariance and correlation derivations
- [x] Linear market regression with residual analysis and rolling Beta
- [~] Bootstrap confidence intervals and hypothesis testing
- [ ] Z-score and mean reversion
- [ ] Monte Carlo simulation
- [ ] Principal component analysis
- [ ] Bayesian updating
- [ ] Markov or hidden-state market regimes
- [ ] Interactive formulas linked to real data

Completion standard: each model includes a formula, intuitive explanation, assumptions, interactive experiment, result and limitation.

## 5. Professional chart research

- [x] Candlestick chart, volume and moving averages
- [ ] RSI, MACD and Bollinger Band panels
- [ ] Buy/sell markers and trade inspection
- [ ] Time-range and interval controls
- [ ] Multi-asset comparison
- [x] Configurable 2-panel and 4-panel comparison layouts
- [ ] Synchronized date range and crosshair across charts
- [~] Compare price, normalized return, drawdown, volatility and volume side by side
- [ ] Small-multiple charts for sectors and watchlists
- [ ] Drawdown chart and underwater duration
- [ ] Rolling volatility, correlation, Alpha and Beta
- [ ] Event overlays for earnings, macro releases and news

Completion standard: charts support research questions rather than merely imitating a trading terminal.

## 5A. Security universe & discovery

- [ ] Expand from the starter list to a curated liquid U.S. stock and ETF universe
- [ ] Search by ticker, company, sector and theme
- [ ] Watchlists and research collections
- [ ] Market-cap, liquidity and data-quality filters
- [ ] Sector, industry and theme membership tables
- [ ] Survivorship-bias-aware historical universe snapshots
- [ ] Reproducible screener results with saved criteria

Completion standard: users can define and reproduce the exact group of securities used in an experiment.

## 6. Parameter stability & validation

- [~] Basic parameter grid search
- [ ] Train/validation/test separation
- [ ] Walk-forward out-of-sample testing
- [ ] Parameter heatmaps and response surfaces
- [ ] Stable-region detection
- [ ] Overfitting warnings
- [ ] Transaction-cost and slippage stress tests
- [ ] Bootstrap confidence intervals
- [ ] Results across bull, bear, sideways and high-volatility markets

Completion standard: no strategy is called successful solely because it fits one historical period.

## 7. News & event research

- [ ] Licensed/authorized news data source
- [ ] Source, ticker and publication-time validation
- [ ] Bilingual sentiment and confidence score
- [ ] Earnings, macro, regulatory and company-event classification
- [ ] Event-study windows and cumulative abnormal return
- [ ] Technical-only vs technical-plus-news controlled experiment
- [ ] False, duplicated, stale and conflicting-news handling
- [ ] Citation trail for every news-derived signal

Completion standard: test whether news adds out-of-sample explanatory value after market and sector effects are controlled.

## 8. Portfolio research

- [ ] Multi-asset portfolio builder
- [ ] Correlation and covariance matrices
- [ ] Equal-weight benchmark
- [ ] Minimum-variance portfolio
- [ ] Maximum-Sharpe portfolio
- [ ] Efficient frontier
- [ ] Risk contribution and concentration
- [ ] Monte Carlo portfolio simulation
- [ ] Rebalancing and turnover costs

Completion standard: evaluate diversification and portfolio risk rather than only isolated stock signals.

## 9. Paper trading & operational safety

- [ ] Signal-only mode
- [ ] Alpaca paper account integration with `paper=True` enforced
- [ ] Position, order and execution reconciliation
- [ ] Duplicate-order protection
- [ ] Position, daily-loss and total-exposure limits
- [ ] Emergency stop and data-quality circuit breaker
- [ ] Daily paper-trading report
- [ ] Backtest vs paper-execution comparison

Completion standard: unattended paper execution remains auditable, bounded and recoverable. Live trading is outside the student-research milestone.

## 10. Research outputs

- [ ] Daily research journal
- [ ] Weekly strategy review
- [ ] Monthly performance report
- [ ] Reproducible experiment catalog
- [ ] English research paper
- [ ] Research poster
- [ ] Three-minute demonstration video
- [ ] Polished GitHub repository
- [ ] Website methodology and limitations pages
- [ ] Final results with positive and negative findings

## 11. Multi-market expansion

- [ ] Market-neutral data model for symbols, currencies, calendars and time zones
- [ ] Hong Kong equities and major Hang Seng benchmarks
- [ ] Corporate-action and currency-conversion handling for Hong Kong equities
- [ ] Foreign exchange pairs and 24-hour market sessions
- [ ] Market-specific transaction costs, spreads and trading rules
- [ ] Cross-market normalized-return comparison
- [ ] Currency-adjusted portfolio performance
- [ ] Data-source licensing and coverage documentation for every market

Completion standard: each added market has correct calendars, currencies, costs, benchmarks and data-quality documentation; U.S. assumptions are never silently reused.

## Proposed central research question

> Can explainable technical, sector, and news signals improve risk-adjusted performance in U.S. equities when evaluated using walk-forward out-of-sample testing?

## Development principles

1. Add complexity only when it answers a research question.
2. Preserve failed experiments and negative findings.
3. Separate model selection from out-of-sample evaluation.
4. Prevent look-ahead, survivorship and publication-time bias.
5. Include realistic costs and execution assumptions.
6. Keep every automated decision explainable and auditable.
7. Never store credentials in source control.
8. Keep paper trading separate from any future live-trading system.
