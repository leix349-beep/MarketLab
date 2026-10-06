# MarketLab

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

One question I am exploring is whether simple, explainable signals can improve risk-adjusted results after realistic costs and out-of-sample testing.

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

Then open `http://localhost:8501`.

## Notes

Signals are calculated from information available at the time and are executed at the next trading day's open. Generated data and experiment records stay local by default.

The current results are still historical backtests. They may be affected by parameter choice, data quality, survivorship bias, and changing market conditions. The next major step is walk-forward out-of-sample testing.

See [`ROADMAP.md`](ROADMAP.md) for the research plan.

<details>
<summary><strong>中文简介</strong></summary>

MarketLab 是我将数学知识与金融数据结合起来制作的双语股票研究网站。我用它测试交易规则、比较股票和板块，并记录成功与失败的实验。

目前网站包括股票图表、技术指标、历史回测、交易记录、板块研究、资产比较、策略比较和回归分析。它是学生研究项目，不提供投资建议，也不会提交订单。

我正在研究的一个问题是：在计入交易成本并进行样本外检验后，简单且可解释的信号能否改善风险调整后的结果。

</details>

## Copyright

Copyright © 2026 Xiang. All rights reserved.

Published for educational review and portfolio demonstration. Reproduction, redistribution, or derivative use requires written permission.
