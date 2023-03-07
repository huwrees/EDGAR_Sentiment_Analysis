import requests

def write_page(url:str, filepath:str) -> None:
    
    '''takes a url and writes the html to a file specified by the provided path
    url: str
    filepath: str'''
    
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})    #request
    
    if r.status_code != 200:                                             #check if response is valid
        raise Exception('Bad Request: Archives')
        
    html_str = r.text                                               #get text of response

    with open(filepath, 'w') as f:                                  #write html to file
        f.write(html_str)

        
def download_files_10k(ticker:str, dest_folder:str) -> None:
    
    '''takes a ticker (4 character string) and writes all 10-K files from that
    ticker to html files in the specified folder
    ticker: 4 character string -> raises an exception if not found
    dest_folder: str'''
    
    #test and cleaning of input data
    if type(ticker) != str or len(ticker) != 4 or type(dest_folder) != str:
        raise Exception('incorrect input')
        
    if dest_folder[-1] != '\\':
        dest_folder += '\\' 
    
    r = requests.get('https://www.sec.gov/files/company_tickers.json')
    
    if r.status_code != 200:                                             #check if response is valid
        raise Exception('Bad Request: Company Tickers')
    
    test = True
    ticker_dict = r.json()
    for entity in ticker_dict:
        if ticker.lower() == ticker_dict[entity]['ticker'].lower():
            cik_short = f'{ticker_dict[entity]["cik_str"]}'
            cik_long = f'{ticker_dict[entity]["cik_str"]:010d}'
            test = False
            break
        
    if test:
        raise Exception('Input ticker not recognised')

    r = requests.get(fr'https://data.sec.gov/submissions/CIK{cik_long}.json',headers={"User-Agent": "Mozilla/5.0"})
    
    if r.status_code != 200:                                             #check if response is valid
        raise Exception('Bad Request: Submissions')
        
    full_list = r.json()['filings']['recent']
    ten_k_list = []
    
    for item in zip(full_list['form']
                    ,full_list['accessionNumber']
                    ,full_list['filingDate']
                    ,full_list['primaryDocument']):
        if item[0] == '10-K':
            ten_k_list.append(list(item))
    
    for item in ten_k_list:
        url = fr'https://www.sec.gov/Archives/edgar/data/{cik_short}/{item[1].replace("-","")}/{item[3]}'
        date = item[2]
        write_page(url, dest_folder+f'{ticker}_10-k_{date}.html')