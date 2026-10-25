# MarketLab Research Cost Model

This cost model is mandatory for new strategy candidates. The assumptions are fixed stress scenarios, not claims about a specific broker, ETF, account, or current interest rate.

| Scenario | Commission | Half-spread | Slippage | One-way trading cost | Annual fund expense | Annual cash yield |
|---|---:|---:|---:|---:|---:|---:|
| Base | 0 bp | 1 bp | 2 bp | 3 bp | 0.15% | 3.00% |
| Adverse | 1 bp | 5 bp | 10 bp | 16 bp | 0.60% | 0.00% |

For every evaluation:

1. Trading cost equals one-way portfolio turnover multiplied by commission, half-spread and slippage.
2. Fund expenses are charged to invested ETF exposure each evaluation period.
3. Uninvested exposure earns the scenario's cash yield.
4. Results must be reported under both scenarios. A candidate cannot pass using the base scenario alone.
5. All results are **pre-tax**. Taxes are excluded because they depend on jurisdiction, account type, holding period and investor circumstances.

Legacy MarketLab results used a single 0.10% turnover fee and zero cash yield. They remain historical references and cannot be promoted under this cost model.
