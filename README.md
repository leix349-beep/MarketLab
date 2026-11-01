# MarketLab

> **Version 1.0 is complete and frozen.** It remains online as a reproducible price-signal research archive. No tested candidate passed the full promotion gates, and none is approved for live trading. Future expectations, earnings and capital-flow research will be developed separately as MarketLab 2.0.

MarketLab is a bilingual stock research website I built to connect ideas from mathematics with financial data. I use it to test trading rules, compare stocks and sectors, and keep a record of both successful and unsuccessful experiments.

This is a student research project, not an investing service. It uses historical data and does not place orders.

## What it includes

- Stock charts, technical indicators, backtests, and trade logs
- U.S. sector performance research
- Multi-asset return, risk, and correlation comparisons
- Side-by-side strategy experiments
- A regression lab for Alpha, Beta, R², residuals, and confidence intervals
- Automated weekday market snapshots recorded after the U.S. market close
- English and Chinese interfaces

The final 1.0 question was whether simple, explainable price signals could improve risk-adjusted results after realistic costs and time-ordered validation. The strongest frozen baseline produced an 8.28% historical annualized return, 0.94 Sharpe ratio and -9.59% maximum drawdown under base costs. It did not meet the full promotion standard and remains `HOLD_NOT_PROMOTED`.

See [`V1_FINAL_STATUS.md`](V1_FINAL_STATUS.md) for the final evidence, failed experiments and the migration boundary for MarketLab 2.0.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Then open `http://localhost:8501`.

## Notes

Signals are calculated from information available at the time and are executed at the next trading day's open. Interactive experiment records stay local by default; explicitly published research snapshots are versioned in this repository.

The results are historical backtests. They may be affected by parameter choice, data quality, survivorship bias, and changing market conditions. Version 1.0 will not receive additional strategy tuning.

See [`ROADMAP.md`](ROADMAP.md) for the research plan.

<details>
<summary><strong>中文简介</strong></summary>

MarketLab 是我将数学知识与金融数据结合起来制作的双语股票研究网站。我用它测试交易规则、比较股票和板块，并记录成功与失败的实验。

目前网站包括股票图表、技术指标、历史回测、交易记录、板块研究、资产比较、策略比较和回归分析。它是学生研究项目，不提供投资建议，也不会提交订单。

1.0版本现已冻结，作为可复现的价格信号研究档案保留。最好的冻结基线在基础成本下历史年化收益为8.28%、Sharpe为0.94、最大回撤为-9.59%，但没有通过完整晋级标准，也不用于真实交易。财报预期与资金轮动研究将转入独立的MarketLab 2.0。

</details>

## Copyright

Copyright © 2026 Xiang. All rights reserved.

Published for educational review and portfolio demonstration. Reproduction, redistribution, or derivative use requires written permission.
