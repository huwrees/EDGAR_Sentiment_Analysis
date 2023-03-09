# ref_data.py

from yahoofinancials import YahooFinancials
import pandas as pd

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
    
    if type(tickers) == str:                                    # if a single ticker (string) is passed through convert to list
        tickers = [tickers]

    data = pd.DataFrame()
    for ticker in tickers:
        yahoo_financials = YahooFinancials(ticker)
        ticker_data = yahoo_financials.get_historical_price_data(start_date, end_date, 'daily')
        ticker_data = pd.DataFrame(ticker_data[ticker]['prices'])
        ticker_data['1daily_return'] = ticker_data['close'].pct_change(periods=1).shift(-1)
        ticker_data['2daily_return'] = ticker_data['close'].pct_change(periods=2)
        ticker_data['3daily_return'] = ticker_data['close'].pct_change(periods=3)
        ticker_data['5daily_return'] = ticker_data['close'].pct_change(periods=5)
        ticker_data['10daily_return'] = ticker_data['close'].pct_change(periods=10)
        ticker_data['Symbol'] = ticker
        data = data.append(ticker_data, sort=False)
    data = data.reset_index()
    data = data[['formatted_date', 'high', 'low', 'close', 'volume', '1daily_return', '2daily_return', '3daily_return', '5daily_return', '10daily_return', 'Symbol']]
    data = data.rename(columns={'formatted_date': 'Date', 'high': 'High', 'low': 'Low', 'close': 'Close'})
    
    return data




def get_sentiment_word_dict():
    '''
    Returns a dictionary containing the LM sentiment words. The keys for the dictionary are the 
    sentiments, and the values will be a list of words associated with that particular sentiment.
    
    Note: Loughran-McDonald MasterDictionary excel file must be in same directory as module.
    '''
    import pandas as pd
    df = pd.read_excel('Loughran-McDonald_MasterDictionary_1993-2021.xlsx')
    
    sentiment_dict = {}

    
    for column in df.columns[1:]:
        
        words = df.loc[df[column] != 0, 'Word'].tolist()
        sentiment_dict[column] = words
    
    return sentiment_dict














