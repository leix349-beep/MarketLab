# MarketLab

**A bilingual, explainable equity-research platform built as a student research project.**

MarketLab 把数学、金融研究和可复现实验放在同一个网站中。它不是“荐股软件”，而是一套用来提出假设、回测策略、比较资产、检查风险并保存研究证据的学习平台。当前版本只使用历史数据，**不会提交真实或模拟订单**。

## Research question / 研究问题

> Can explainable technical and sector signals improve risk-adjusted performance in U.S. equities when evaluated without look-ahead bias?

中文：在避免前视偏差、计入交易成本并进行样本外检验时，可解释的技术与板块信号能否改善美股策略的风险调整后表现？

## Current modules / 当前模块

- **Stock Research**：K线、成交量、技术指标、回测、交易记录、参数实验与每日研究报告
- **Market Sectors**：11 个标准行业 ETF 的相对强弱、收益和波动率比较
- **Asset Comparison**：最多四个资产的标准化表现、回撤、滚动波动率和相关矩阵
- **Strategy Lab**：在相同数据与成本假设下比较 Buy & Hold、趋势、均值回归、突破和 Trend + RSI
- **Regression Lab**：OLS 市场模型、Beta、年化 Alpha、R²、残差、滚动 Beta 和 bootstrap 置信区间

## Research design / 研究设计

- 指标只使用当时已知的历史信息，信号在下一交易日开盘执行
- 所有策略使用相同的数据区间、费用与滑点假设
- 每次正式运行可以保存参数、数据来源时间、结果与复现信息
- 同时保留正面、负面和失败实验，避免只展示“最好看”的结果
- 当前结果仍属于历史回测；尚未完成的严格检验会在界面与路线图中明确标出

## Data and reproducibility / 数据与复现

运行记录保存在 `research_records/`：

- `raw_data/`：带抓取时间的原始行情快照
- `experiment_manifests/`：参数和复现信息
- `parameter_experiments/`：参数及数学实验结果
- `sector_snapshots/`：板块研究快照
- `daily_reports/`：每日研究报告
- `experiments.csv`：实验索引

这些运行产物默认不上传 GitHub，仓库只公开源代码、方法说明和不含隐私的示例结果。

## GitHub 安全

`.gitignore` 已排除虚拟环境、缓存和密钥文件。不要把 `.env`、`secrets.toml`、Alpaca 密钥或任何账户信息提交到 GitHub。

## 启动（Windows）

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m streamlit run app.py
```

打开 `http://localhost:8501`。网站支持中英文切换；所有收益结果均为历史模拟，不构成投资建议。

## Limitations / 局限

- 免费行情源可能延迟、修订或短暂不可用
- 当前策略仍需 walk-forward 样本外检验、稳定性分析和更严格的统计检验
- 结果可能受到参数选择、幸存者偏差和市场状态变化影响
- Alpha、Beta 与相关性描述历史关系，不证明因果关系

## 下一阶段

1. Walk-forward 样本外验证与参数稳定性热力图
2. 投资组合、有效前沿与 Monte Carlo 数学实验
3. 有来源与时间戳的新闻事件研究
4. 周报、研究论文、海报与可公开演示的结果页面

完整的长期模块、完成标准和研究原则见 [`ROADMAP.md`](ROADMAP.md)。

准备公开测试时，请按 [`DEPLOYMENT.md`](DEPLOYMENT.md) 逐项检查。

## Copyright / 版权声明

Copyright © 2026 Xiang. All rights reserved.

This repository is published for educational review and portfolio demonstration. No permission is granted to reproduce, redistribute, or create derivative works without written authorization.

本项目仅用于教育评审、研究展示与个人作品集展示。未经作者书面许可，不得复制、重新分发或创作衍生作品。
