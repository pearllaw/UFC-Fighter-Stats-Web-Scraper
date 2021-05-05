import requests, time, random, re
import datetime
from string import ascii_lowercase as alphabet
from itertools import cycle
from bs4 import BeautifulSoup as bs
import pandas as pd 
from multiprocessing.pool import ThreadPool
from tqdm import tqdm
from fake_useragent import UserAgent
from proxies import *

MAX_PROCESSES = 6
MAX_THREADS = 10

"""Asynchronous method: 
~4.52 seconds to get all fighter urls
~2576.96 seconds = (~43 mins) to get all fighter stats"""

# Initialize data storage
urls = []
fighter_urls = {}
f_data = []

class ProxyError(Exception):
    """Exception raised when proxy attempts exceeded"""
    def __init__(self, url, message):
        self.url = url
        self.message = message 

def make_request(url, referer, tolerance=10):
    """Make request to each fighter page by rotating proxies & using random UA"""
    with requests.Session() as session:
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
            # Iterate through proxy_list and assign next element from iterable to proxy
            proxy = next(proxy_pool)
            proxies = {
                'http': 'http://' + proxy,
                'https': 'https://' + proxy
            }
            try: 
                # Send request 
                response = session.get(url, headers=headers, proxies=proxies)
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
    # Initialize f_stats dictionary
    f_stats = dict.fromkeys(['Name', 'DOB', 'Win', 'Lose', 'Draw', 'NC', 'Height', 
    'Weight', 'Reach', 'Stance', 'SLPM', 'Str_Acc', 'SAPM', 'Str_Def', 'TD_Avg', 
    'TD_Acc', 'TD_Def', 'Sub_Avg', 'Fights'])
    f_stats['Fights'] = []
    # Make request
    r = make_request(url, referer)
    # Parse response
    soup = bs(r.text, 'lxml')
    name = soup.find('span', class_='b-content__title-highlight').text.strip()
    f_stats['Name'] = name
    record = soup.find('span', class_='b-content__title-record').text.strip()
    # Clean record data
    splitted = re.split('[-()NC]', record[8:])
    record_arr = list(filter(None, splitted))
    win = record_arr[0]
    f_stats['Win'] = win
    lose = record_arr[1]
    f_stats['Lose'] = lose
    draw = record_arr[2]
    f_stats['Draw'] = draw
    nc = record_arr[3] if len(record_arr) == 4 else '0'
    f_stats['NC'] = nc

    fight_details = soup.find_all('li', class_='b-list__box-list-item')
    for fd in fight_details:
        keyword = fd.i.text.strip().lower()
        text = fd.i.next_sibling.strip()
        if keyword == 'height:':
            f_stats['Height'] = text
        elif keyword == 'weight:':
            f_stats['Weight'] = text
        elif keyword == 'reach:':
            f_stats['Reach'] = text
        elif keyword == 'stance:': 
            f_stats['Stance'] = text
        elif keyword == 'dob:':
            f_stats['DOB'] = text
        elif keyword == 'slpm:':
            f_stats['SLPM'] = text
        elif keyword == 'str. acc.:':
            f_stats['Str_Acc'] = text
        elif keyword == 'sapm:':
            f_stats['SAPM'] = text
        elif keyword == 'str. def:':
            f_stats['Str_Def'] = text
        elif keyword == 'td avg.:':
            f_stats['TD_Avg'] = text 
        elif keyword == 'td acc.:':
            f_stats['TD_Acc'] = text
        elif keyword == 'td def.:':
            f_stats['TD_Def'] = text
        elif keyword == 'sub. avg.:':
            f_stats['Sub_Avg'] = text 

    table_body = soup.find('tbody')
    for row in table_body.find_all('tr', 'b-fight-details__table-row'):
        event = dict()
        future_event = row.find_all('td')[0].i.i.text == 'next'
        if not future_event:
            event['Event'] = row.find_all('td')[6].p.a.text.strip()
            event['Date'] = row.find_all('td')[6].p.findNextSibling('p').text.strip()
            event['W/L'] = row.find_all('td')[0].i.i.text
            event['Opponent'] = row.find_all('td')[1].p.findNextSibling('p').a.text.strip()
            event['KD'] = row.find_all('td')[2].p.text.strip() # kd = knockdowns
            event['Opp_KD'] = row.find_all('td')[2].p.findNextSibling('p').text.strip()
            event['Str'] = row.find_all('td')[3].p.text.strip() # str = significant strikes
            event['Opp_Str'] = row.find_all('td')[3].p.findNextSibling('p').text.strip()
            event['TD'] = row.find_all('td')[4].p.text.strip() # td = takedowns
            event['Opp_TD'] = row.find_all('td')[4].p.findNextSibling('p').text.strip()
            event['Sub'] = row.find_all('td')[5].p.text.strip() # sub = submission attempts
            event['Opp_Sub'] = row.find_all('td')[5].p.findNextSibling('p').text.strip()
            event['Method'] = row.find_all('td')[7].p.text.strip()
            event['Round'] = row.find_all('td')[8].p.text.strip()
            event['Time'] = row.find_all('td')[9].p.text.strip()
            f_stats['Fights'].append(event)
    # Append fighter stats into f_data list
    f_data.append(f_stats)

def parse_fighter_urls(url):
    # Make request
    try:
        r = requests.get(url) 
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)   
    # Create Beautiful Soup object that takes HTML content and parser
    soup = bs(r.text, 'lxml')
    # Parse and return each fighter url from alphabetical page url
    links = soup.select('a.b-link')
    hrefs = [l['href'] for l in links]
    unique_links = list(set(hrefs))
    return {url : unique_links}

def fetch_fighter_urls():
    """Retrieve all fighter urls = {alphabet page url : all corresponding fighter urls}"""
    with ThreadPool(processes=MAX_PROCESSES) as tp:
        for res in [tp.apply_async(parse_fighter_urls, (url, )) for url in urls]:
            fighter_urls.update(res.get())

def async_scraping_tasks():
    """Scrape stats from all fighter urls"""
    start = time.time()
    for referer, urls in fighter_urls.items():
        # Get new list of proxies if iteration time >= 10 minutes
        if int(time.time() - start) >= 600: 
            get_proxy()
            start = time.time()
        with tqdm(total=len(urls)) as pbar:
            with ThreadPool(processes=MAX_THREADS) as tp:
                def callback(*args):
                    pbar.update()
                    return
                results = [tp.apply_async(parse_fighter_data, args=(url, referer), callback=callback) for url in urls]
                results = [r.get() for r in results]
    
if __name__ == '__main__':  
    # Fetch all page urls by alphabet
    urls = [f"http://ufcstats.com/statistics/fighters?char={ch}&page=all" for ch in alphabet]
    # Populate list of proxies 
    get_proxy()
    
    now = time.time()
    fetch_fighter_urls()
    print(f"{time.time() - now} seconds to get all fighter urls")
    
    now = time.time()
    async_scraping_tasks()
    print(f"{time.time() - now} seconds to get all fighter stats")

    # Create DataFrame from fdata dictionary 
    df = pd.DataFrame(f_data)
    df1 = pd.concat([pd.DataFrame(x) for x in df['Fights']], keys=df.index).reset_index(level=1, drop=True)
    df = df.drop('Fights', axis=1).join(df1)
    # Save data into csv
    datetime = datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
    df.to_csv(f"fighter_stats_{datetime}.csv", index=False)