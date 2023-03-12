import requests
import time

user_email = 'gregsmith@kubrickgroup.com'

def full_download(ticker_list:list[str], dest_folder:str, user_email = user_email, min_date = None, max_date = None, report = '10-K') -> None:
    
    '''
    takes a list of company tickers and writes all reports of a specific type, between specific dates, to a
    destination folder.
    ticker_list: list of strings of tickers for the companies being examined
    dest_folder: string of the destination folder
    user_email:string
    min_date: str in 'YYYY-MM-DD' format can specify the earliest date records should be included
    max_date: str in 'YYYY-MM-DD' format  can specify the latest date records should be included
    report: str -> specifies the type of report to run
    '''
   
    missing_tickers = []
    all_tickers = []

    r = get_request('https://www.sec.gov/files/company_tickers.json', 'Company Tickers', user_email).json()
    

    for key in r:
        all_tickers.append(r[key]['ticker'].lower())

    for ticker in ticker_list:
        if ticker.lower() not in all_tickers:
            missing_tickers.append(ticker.upper())

    if len(missing_tickers) != 0:
        raise Exception(f'The following tickers were not available from the SEC API: {", ".join(missing_tickers)}')

    for ticker in ticker_list:
        download_files_10k(ticker, dest_folder, user_email, min_date, max_date, report)



def download_files_10k(ticker:str, dest_folder:str, user_email = user_email, min_date = None, max_date = None, report = '10-K') -> None:
    
    '''
    takes a ticker and writes all files from that ticker to html files in the specified folder.
    ticker:string -> raises an exception if not found
    dest_folder: string
    user_email: string
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
    r = get_request('https://www.sec.gov/files/company_tickers.json', 'Company Tickers', user_email)
    
    #process and return CIK as string and string with leading zeros 
    cik_short, cik_long = cik_get(r, ticker)
    
    #request submissions list
    r = get_request(fr'https://data.sec.gov/submissions/CIK{cik_long}.json', 'Submissions', user_email)
      
    #full list of 10-K reports with relevant extensions
    ten_k_list = submissions(r, min_date, max_date, report, user_email)
    
    i_url = fr'https://www.sec.gov/Archives/edgar/data/'
    #request content of 10-K reports and write to file
    for item in ten_k_list:
        date = item[2]
        try:
            if item[3] != '':
                url = fr'{i_url}{cik_short}/{item[1].replace("-","")}/{item[3]}'
                write_page(url, dest_folder+f'{ticker}_{report}_{date}.html', user_email)
            else:
                url = fr'{i_url}{cik_short}/{item[1]}.txt'
                write_page(url, dest_folder+f'{ticker}_{report}_{date}.html', user_email)
        except:
            url = fr'{i_url}{cik_short}/{item[1].replace("-","")}/{item[1]}.txt'
            write_page(url, dest_folder+f'{ticker}_{report}_{date}.html', user_email)



def write_page(url:str, filepath:str, user_email:str) -> None:
    
    '''
    takes a url and writes the html to a file specified by the provided path
    url: string
    user_email: string
    filepath: string
    '''
    
    r = get_request(url, 'Archives', user_email)    #request        
        
    html_str = r.text                                               #get text of response

    with open(filepath, 'w') as f:                                  #write html to file
        f.write(html_str)


        
def get_request(url:str, section:str, user_email:str):
    
    '''
    takes a url and returns the response via the requests get method. Raises a specific exception
    if the response is anything except 200. Headers are specified externally. Sleep method has been
    included to limit request volume.
    url:string
    user_email:string
    section: string
    headers: dictionary of the form {"User-Agent": "gregsmith@kubrickgroup.com"}
    '''
    headers = {'User-Agent': user_email}
    
    r = requests.get(url,headers=headers)
    
    if r.status_code != 200:                                             #check if response is valid
        raise Exception(f'Bad Request: {section}')
    
    time.sleep(.1)
    
    return r



def cik_get(r, ticker:str):
    
    '''
    takes the response from the mapping document and identifies the CIK associated with that ticker.
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
        raise Exception(f'Input ticker {ticker} not recognised')


def submissions(r, min_date:str, max_date:str, report:str, user_email:str) -> list[(str,str,str,str)]:
    
    '''
    takes the response from the company filings and returns this as a list of tuples that represent the required
    values to make additional API calls.
    r: response object
    min_date: str in 'YYYY-MM-DD' format can specify the earliest date records should be included
    max_date: str in 'YYYY-MM-DD' format  can specify the latest date records should be included
    report: str -> specifies the type of report to run
    user_email:string
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
        r = get_request(fr'https://data.sec.gov/submissions/{file["name"]}', 'Older Filings', user_email).json()
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
