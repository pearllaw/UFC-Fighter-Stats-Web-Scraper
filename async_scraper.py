import requests, time, random, re
import datetime
from itertools import cycle
from string import ascii_lowercase as alphabet
from bs4 import BeautifulSoup
import pandas as pd 
from multiprocessing.pool import ThreadPool
from fake_useragent import UserAgent
from proxies import *

MAX_PROCESSES = 10
MAX_THREADS = 25 

"""Asynchronous method: 
~4.52 seconds to get all fighter urls
~334.57 seconds to get all fighter stats"""

# Initialize data storage
urls = []
fighter_urls = {}
fdata = {
    'name': [],
    'win': [],
    'lose': [],
    'draw': [],
    'nc': [],
    'height': [],
    'weight': [],
    'reach': [],
    'stance': [],
    'dob': [],
    'slpm': [],
    'str_acc': [],
    'sapm': [],
    'str_def': [],
    'td_avg': [],
    'td_acc': [],
    'td_def': [],
    'sub_avg': []
}

class ProxyError(Exception):
    """Exception raised when proxy attempts exceeded"""
    def __init__(self, url, message):
        self.url = url
        self.message = message 

def make_request(url, referer, tolerance=10):
    """Make request to each fighter page by rotating proxies & using random UA"""
    with requests.Session() as req:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
            "Accept-Encoding": "gzip, deflate", 
            "Accept-Language": "en-US,en;q=0.9", 
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "DNT": "1", 
            "Host": "ufcstats.com", 
            "Referer": referer,
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": UserAgent().random
        }
        dead_proxy_count = 0
        proxy_pool = cycle(proxy_list)
        while dead_proxy_count < tolerance:
            if len(proxy_list) < 1:
                get_proxy()
            # Iterate through proxy_list and assign next element from iterable to proxy
            proxy = next(proxy_pool)
            proxies = {
                'http': 'http://' + proxy,
                'https': 'https://' + proxy
            }
            try: 
                # Send request 
                response = req.get(url, headers=headers, proxies=proxies)
                if response.status_code == 200: 
                    return response
            except: 
                # Retry with different proxy  
                dead_proxy_count += 1
            else: 
                # Delay scraping for 1-3 sec if status code is not 200, but proxy is not dead
                time.sleep(random.randint(1, 3))
        raise ProxyError(url=url, message="Burned through too many proxies")

def parse_fighter_data(url, referer):
    """Parse each fighter page to get summary stats"""
    r = make_request(url, referer)
    soup = BeautifulSoup(r.text, 'lxml')
    name = soup.find('span', class_='b-content__title-highlight').text.strip()
    fdata['name'].append(name)

    record = soup.find('span', class_='b-content__title-record').text.strip()
    # Clean record data
    splitted = re.split('[-()NC]', record[8:])
    record_arr = list(filter(None, splitted))
    win = record_arr[0]
    fdata['win'].append(win)
    lose = record_arr[1]
    fdata['lose'].append(lose)
    draw = record_arr[2]
    fdata['draw'].append(draw)
    nc = record_arr[3] if len(record_arr) == 4 else '0'
    fdata['nc'].append(nc)
    
    fight_details = soup.find_all('li', class_='b-list__box-list-item')
    for fd in fight_details:
        keyword = fd.i.text.strip().lower()
        text = fd.i.next_sibling.strip()
        if keyword == 'height:':
            height = text
            fdata['height'].append(height)
        elif keyword == 'weight:':
            weight = text
            fdata['weight'].append(weight)
        elif keyword == 'reach:':
            reach = text
            fdata['reach'].append(reach)
        elif keyword == 'stance:': 
            stance = text
            fdata['stance'].append(stance)
        elif keyword == 'dob:':
            dob = text
            fdata['dob'].append(dob)
        elif keyword == 'slpm:':
            slpm = text
            fdata['slpm'].append(slpm)
        elif keyword == 'str. acc.:':
            str_acc = text
            fdata['str_acc'].append(str_acc)
        elif keyword == 'sapm:':
            sapm = text
            fdata['sapm'].append(sapm)
        elif keyword == 'str. def:':
            str_def = text 
            fdata['str_def'].append(str_def)
        elif keyword == 'td avg.:':
            td_avg = text 
            fdata['td_avg'].append(td_avg)
        elif keyword == 'td acc.:':
            td_acc = text 
            fdata['td_acc'].append(td_acc)
        elif keyword == 'td def.:':
            td_def = text 
            fdata['td_def'].append(td_def)
        elif keyword == 'sub. avg.:':
            sub_avg = text 
            fdata['sub_avg'].append(sub_avg)

def parse_fighter_urls(url):
    """Parse alphabetical page to get each fighter's url"""
    r = requests.get(url)
    # Throw exception if status code is not 200
    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return "Exception: " + e
    # Create Beautiful Soup object that takes HTML content and parser
    soup = BeautifulSoup(r.text, 'lxml')
    # Extract individual fighter urls into fighter_urls
    links = soup.select('a.b-link')
    hrefs = [l['href'] for l in links]
    unique_links = list(set(hrefs))
    return {url : unique_links}

def fetch_fighter_urls():
    """Retrieve all fighter urls = { alphabet page url : all corresponding fighter urls }"""
    with ThreadPool(MAX_PROCESSES) as tp:
        for res in tp.map(parse_fighter_urls, urls):
            fighter_urls.update(res)

def async_scraping_tasks():
    """Scrape stats from all fighter urls"""
    for referer, urls in fighter_urls.items():
        with ThreadPool(MAX_THREADS) as tp:
            tasks = [tp.apply_async(parse_fighter_data, args=(url, referer)) for url in urls]
            results = [t.get() for t in tasks]

if __name__ == '__main__':
    # Fetch all page urls by alphabet
    urls = [f"http://ufcstats.com/statistics/fighters?char={ch}&page=all" for ch in alphabet]
    
    # Populate list of proxies 
    get_proxy()
    
    t0 = time.time()
    fetch_fighter_urls()
    t1 = time.time()
    print(f"{t1-t0} seconds to get all fighter urls")
   
    t0 = time.time()
    async_scraping_tasks()
    t1 = time.time()
    print(f"{t1-t0} seconds to get all fighter stats")

    # Place fdata dictionary object into DataFrame
    df = pd.DataFrame(dict([ (k, pd.Series(v)) for k, v in fdata.items() ]))

    # Save data into csv
    datetime = datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    df.to_csv(f"fighter_stat_summary_{datetime}.csv", index=False)