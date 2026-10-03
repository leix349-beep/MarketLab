SECTOR_ETFS = {
    "Technology": "XLK", "Financials": "XLF", "Health Care": "XLV",
    "Energy": "XLE", "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP", "Industrials": "XLI",
    "Communication Services": "XLC", "Utilities": "XLU",
    "Real Estate": "XLRE", "Materials": "XLB",
}

ASSETS = {
    "SPY": ("S&P 500 ETF", "Broad Market"), "QQQ": ("Nasdaq-100 ETF", "Broad Market"),
    "IWM": ("Russell 2000 ETF", "Broad Market"), "DIA": ("Dow Jones ETF", "Broad Market"),
    "AAPL": ("Apple", "Technology"), "MSFT": ("Microsoft", "Technology"),
    "NVDA": ("NVIDIA", "Technology"), "AVGO": ("Broadcom", "Technology"),
    "ORCL": ("Oracle", "Technology"), "AMD": ("AMD", "Technology"),
    "AMZN": ("Amazon", "Consumer Discretionary"), "TSLA": ("Tesla", "Consumer Discretionary"),
    "HD": ("Home Depot", "Consumer Discretionary"), "MCD": ("McDonald's", "Consumer Discretionary"),
    "GOOGL": ("Alphabet", "Communication Services"), "META": ("Meta Platforms", "Communication Services"),
    "NFLX": ("Netflix", "Communication Services"), "JPM": ("JPMorgan Chase", "Financials"),
    "BAC": ("Bank of America", "Financials"), "V": ("Visa", "Financials"),
    "MA": ("Mastercard", "Financials"), "LLY": ("Eli Lilly", "Health Care"),
    "UNH": ("UnitedHealth", "Health Care"), "JNJ": ("Johnson & Johnson", "Health Care"),
    "XOM": ("Exxon Mobil", "Energy"), "CVX": ("Chevron", "Energy"),
    "WMT": ("Walmart", "Consumer Staples"), "COST": ("Costco", "Consumer Staples"),
    "CAT": ("Caterpillar", "Industrials"), "GE": ("GE Aerospace", "Industrials"),
}

for sector, ticker in SECTOR_ETFS.items():
    ASSETS.setdefault(ticker, (f"{sector} Select Sector ETF", sector))

def asset_label(ticker):
    name, sector = ASSETS[ticker]
    return f"{ticker} · {name} · {sector}"

def sector_etf_for(ticker):
    sector = ASSETS.get(ticker, ("", "Broad Market"))[1]
    return SECTOR_ETFS.get(sector, "SPY")

