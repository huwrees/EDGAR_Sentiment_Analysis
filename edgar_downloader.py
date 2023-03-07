import requests

def write_page(url, filepath):
    html_str = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text

    with open(filepath, 'w') as f:
        f.write(html_str)

        
def download_files_10k(ticker, dest_folder):
    ticker_dict = requests.get('https://www.sec.gov/files/company_tickers.json').json()
    for entity in ticker_dict:
        if ticker == ticker_dict[entity]['ticker']:
            cik_short = f'{ticker_dict[entity]["cik_str"]}'
            cik_long = f'{ticker_dict[entity]["cik_str"]:010d}'

    full_list = requests.get(fr'https://data.sec.gov/submissions/CIK{cik_long}.json', headers={"User-Agent": "Mozilla/5.0"}).json()
    ten_k_list = []
    
    for n, item in enumerate(full_list['filings']['recent']['form']):
        if full_list['filings']['recent']['form'][n] == '10-K':
            ten_k_list.append([full_list['filings']['recent']['accessionNumber'][n]
                               ,full_list['filings']['recent']['form'][n]
                               ,full_list['filings']['recent']['filingDate'][n]
                               ,full_list['filings']['recent']['primaryDocument'][n]])
            
    for item in ten_k_list:
        url = fr'https://www.sec.gov/Archives/edgar/data/{cik_short}/{item[0].replace("-","")}/{item[3]}'
        date = item[2]
        write_page(url, dest_folder+f'{ticker}_10-k_{date}.html')