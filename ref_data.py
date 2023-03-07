# ref_data.py
def get_sp100():
    """
    Returns a list of all tickers in the S&P100.
    """
    return ["AAPL", "MSFT", "AMZN", "BRK.B", "GOOGL", "UNH", "GOOG", "JNJ", "XOM", "JPM", "NVDA", "PG", "V", "HD", "TSLA", "CVX", "MA", "LLY", "ABBV", "PFE", "MRK", "META", "PEP", "KO", "BAC", "AVGO", "TMO", "COST", "WMT", "MCD", "ABT", "ADBE", "CSCO", "NFLX", "ORCL", "INTC", "CRM", "VZ", "QCOM", "PM", "DHR", "NKE", "C", "UNP", "T", "PNC", "PYPL", "WFC", "NEE", "PDD", "TMUS", "UPS", "ACN", "IBM", "TXN", "HON", "AMGN", "LIN", "LMT", "GILD", "MU", "TGT", "RTX", "AZN", "AON", "BMY", "SBUX", "CME", "LOW", "MDT", "UPS", "GS", "MDT", "MCO", "AMAT", "CAT", "AXP", "ABNB", "BLK", "CVNA", "COP", "CVS", "DOW", "GSK", "LVS", "TM", "ADI", "DUK", "ILMN", "MMM", "SO", "TOT", "AIG", "BIIB", "CL", "D", "DIS", "DUK", "FDX", "GM", "KMB", "MDLZ", "MO", "NEE", "NVO", "PBR", "PSX", "RACE", "SO", "TMX", "UBER", "VLO"]

def get_yahoo_data(start_date, end_date, tickers):
    """
    Downloads yahoo finance data and cosolidates into a table.
    Returns a dataframe.
    """
    import yfinance as yf
    import pandas as pd
    
    data = pd.DataFrame()
    for ticker in tickers:
        ticker_data = yf.download(ticker, start=start_date, end=end_date)
        ticker_data['1daily_return'] = ticker_data['Close'].pct_change(periods=1)
        ticker_data['2daily_return'] = ticker_data['Close'].pct_change(periods=2)
        ticker_data['3daily_return'] = ticker_data['Close'].pct_change(periods=3)
        ticker_data['5daily_return'] = ticker_data['Close'].pct_change(periods=5)
        ticker_data['10daily_return'] = ticker_data['Close'].pct_change(periods=10)
        ticker_data['Symbol'] = ticker
        data = data.append(ticker_data, sort=False)
    data = data.reset_index()
    data = data[['Date', 'High', 'Low', 'Close', 'Volume', '1daily_return', '2daily_return', '3daily_return', '5daily_return', '10daily_return', 'Symbol']]
    
    return data