import requests
import time

s_and_p_100 = ['AAPL', 'ABBV', 'ABT', 'ACN', 'ADBE', 'AIG', 'AMD', 'AMGN', 'AMT', 'AMZN'
               , 'AVGO', 'AXP', 'BA', 'BAC', 'BK', 'BKNG', 'BLK', 'BMY', 'BRK-B', 'C'
               , 'CAT', 'CHTR', 'CL', 'CMCSA', 'COF', 'COP', 'COST', 'CRM', 'CSCO', 'CVS'
               , 'CVX', 'DHR', 'DIS', 'DOW', 'DUK', 'EMR', 'EXC', 'F', 'FDX', 'GD'
               , 'GE', 'GILD', 'GM', 'GOOG', 'GOOGL', 'GS', 'HD', 'HON', 'IBM', 'INTC'
               , 'JNJ', 'JPM', 'KHC', 'KO', 'LIN', 'LLY', 'LMT', 'LOW', 'MA', 'MCD'
               , 'MDLZ', 'MDT', 'MET', 'META', 'MMM', 'MO', 'MRK', 'MS', 'MSFT', 'NEE'
               , 'NFLX', 'NKE', 'NVDA', 'ORCL', 'PEP', 'PFE', 'PG', 'PM', 'PYPL', 'QCOM'
               , 'RTX', 'SBUX', 'SCHW', 'SO', 'SPG', 'T', 'TGT', 'TMO', 'TMUS', 'TSLA'
               , 'TXN', 'UNH', 'UNP', 'UPS', 'USB', 'V', 'VZ', 'WBA', 'WFC', 'WMT', 'XOM']

headers = {'User-Agent': "gregsmith@kubrickgroup.com"}

def write_page(url:str, filepath:str) -> None:
    
    '''takes a url and writes the html to a file specified by the provided path
    url: str
    filepath: str'''
    
    r = get_request(url, 'Archives')    #request        
        
    html_str = r.text                                               #get text of response

    with open(filepath, 'w') as f:                                  #write html to file
        f.write(html_str)

        
def download_files_10k(ticker:str, dest_folder:str, min_date = None, max_date = None, report = '10-K') -> None:
    
    '''takes a ticker and writes all files from that ticker to html files in the specified folder.
    ticker:string -> raises an exception if not found
    dest_folder: str
    min_date: str in 'YYYY-MM-DD' format can specify the earliest date records should be included
    max_date: str in 'YYYY-MM-DD' format  can specify the latest date records should be included
    report: str -> specifies the type of report to run
    '''
    
    #test and cleaning of input data
    if type(ticker) != str or type(dest_folder) != str:
        raise Exception('incorrect input')
        
    if dest_folder[-1] != '\\':
        dest_folder += '\\' 
    
    #request for company ticker mappings
    r = get_request('https://www.sec.gov/files/company_tickers.json', 'Company Tickers')
    
    #process and return CIK as string and string with leading zeros 
    cik_short, cik_long = cik_get(r, ticker)
    
    #request submissions list
    r = get_request(fr'https://data.sec.gov/submissions/CIK{cik_long}.json', 'Submissions')
      
    #full list of 10-K reports with relevant extensions
    ten_k_list = submissions(r, min_date, max_date, report)
    
    #request content of 10-K reports and write to file
    for item in ten_k_list:
        date = item[2]
        try:
            if item[3] != '':
                url = fr'https://www.sec.gov/Archives/edgar/data/{cik_short}/{item[1].replace("-","")}/{item[3]}'
                write_page(url, dest_folder+f'{ticker}_{report}_{date}.html')
            else:
                url = fr'https://www.sec.gov/Archives/edgar/data/{cik_short}/{item[1]}.txt'
                write_page(url, dest_folder+f'{ticker}_{report}_{date}.html')
        except:
            url = fr'https://www.sec.gov/Archives/edgar/data/{cik_short}/{item[1].replace("-","")}/{item[1]}.txt'
            write_page(url, dest_folder+f'{ticker}_{report}_{date}.html')
                

        
def get_request(url:str, section:str, headers=headers):
    
    '''takes a url and returns the response via the requests get method. Raises a specific exception
    if the response is anything except 200. Headers are specified externally. Sleep method has been
    included to limit request volume.
    url:string
    section: str
    headers: dictionary of the form {"User-Agent": "gregsmith@kubrickgroup.com"}
    '''
    
    r = requests.get(url,headers=headers)
    
    if r.status_code != 200:                                             #check if response is valid
        raise Exception(f'Bad Request: {section}')
    
    time.sleep(.1)
    
    return r

def cik_get(r, ticker:str) -> (str,str):
    
    '''takes the response from the mapping document and identifies the CIK associated with that ticker.
    If no ticker is found an exception is raised. Returns a tuple consisting of the CIK as a trimmed 
    string and a 10 character string with leading zeros
    r: response object
    ticker: string
    '''
    
    test = True
    ticker_dict = r.json()
    for entity in ticker_dict:
        if ticker.lower() == ticker_dict[entity]['ticker'].lower():
            test = False
            return (f'{ticker_dict[entity]["cik_str"]}',f'{ticker_dict[entity]["cik_str"]:010d}')
    if test:
        raise Exception('Input ticker not recognised')
        
def submissions(r, min_date:str, max_date:str, report:str) -> list[(str,str,str,str)]:
    
    '''takes the response from the company filings and returns this as a list of tuples that represent the required
    values to make additional API calls.
    r: response object
    min_date: str in 'YYYY-MM-DD' format can specify the earliest date records should be included
    max_date: str in 'YYYY-MM-DD' format  can specify the latest date records should be included
    report: str -> specifies the type of report to run
    '''
    
    filings = r.json()['filings']
    
    recent_filings = filings['recent']
    previous_filings = filings['files']
    
    full_filings = {}
    full_filings['form'] = recent_filings['form']
    full_filings['accessionNumber'] = recent_filings['accessionNumber']
    full_filings['filingDate'] = recent_filings['filingDate']
    full_filings['primaryDocument'] = recent_filings['primaryDocument']
    
    for file in previous_filings:
        r = get_request(fr'https://data.sec.gov/submissions/{file["name"]}', 'Older Filings').json()
        full_filings['form'].extend(r['form'])
        full_filings['accessionNumber'].extend(r['accessionNumber'])
        full_filings['filingDate'].extend(r['filingDate'])
        full_filings['primaryDocument'].extend(r['primaryDocument'])

    ten_k_list = []
    
    for item in zip(full_filings['form']
                    ,full_filings['accessionNumber']
                    ,full_filings['filingDate']
                    ,full_filings['primaryDocument']):
        if item[0].lower() == report.lower() and (min_date == None or item[2] >= min_date) and (max_date == None or item[2] <= max_date):
            ten_k_list.append(list(item))
    
    return ten_k_list

def full_download(ticker_list:list[str], dest_folder:str, min_date = None, max_date = None, report = '10-K') -> None:
    
    '''takes a list of company tickers and writes all reports of a specific type, between specific dates, to a
    destination folder.
    ticker_list: list of strings of tickers for the companies being examined
    dest_folder: string of the destination folder
    min_date: str in 'YYYY-MM-DD' format can specify the earliest date records should be included
    max_date: str in 'YYYY-MM-DD' format  can specify the latest date records should be included
    report: str -> specifies the type of report to run
    '''
    
    for ticker in ticker_list:
        download_files_10k(ticker, dest_folder, min_date, max_date, report)