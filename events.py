import requests, time
from string import ascii_lowercase as alphabet
from multiprocessing.pool import ThreadPool
import pandas as pd 
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
from proxies import *
from rotate_requests import *

MAX_THREADS = 10

"""Asynchronous method: 
~1.22 seconds to scrape all event urls
~36.10 seconds to scrape all event data"""

completed_events_url = "http://ufcstats.com/statistics/events/completed?page=all"
event_urls = []
events = [] 
       
def fetch_event_urls():
    """Get list of completed event urls and store in events list"""
    # Make request
    try:
        r = requests.get(completed_events_url) 
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise SystemExit(e)   
    # Parse response
    soup = bs(r.text, 'lxml')
    table_body = soup.select('tbody tr', class_='b-statistics__table-row')
    for row in table_body:
        link = [a['href'] for a in row.select('a')]
        event_urls.extend(link)

def parse_event_details(url):
    # Initialize dictionary to store event data
    e_keys = ('Event', 'Fights')
    event = dict.fromkeys(e_keys)
    event['Fights'] = []
    # Make request
    r = requests.get(url)
    #r = make_request(url, completed_events_url)
    # Parse response
    soup = bs(r.text, 'lxml')
    event['Event'] = soup.find('h2').text.strip()
    for row in soup.select('tbody tr'):
        # Initialize dictionary to store single fight data
        fight = dict()
        fight['F1'] = row.find_all('td')[1].p.text.strip()
        fight['F2'] = row.find_all('td')[1].p.findNextSibling('p').text.strip()
        fight['Weight_Class'] = row.find_all('td')[6].text.strip()
        event['Fights'].append(fight)
    events.append(event)

def async_scrape_events():
    with ThreadPool(processes=MAX_THREADS) as tp:
        with tqdm(total=len(event_urls)) as pbar:
            start = time.time()
            for res in [tp.apply_async(parse_event_details, (ev, )) for ev in event_urls]:
                if int(time.time() - start) >= 600: 
                    get_proxy()
                    start = time.time()
                res.get()
                pbar.update()

if __name__ == '__main__':
    # Populate list of proxies 
    get_proxy()

    now = time.time()
    fetch_event_urls()
    print(f"Took {time.time() - now} seconds to scrape all event urls")
    
    now = time.time()
    async_scrape_events()
    print(f"Took {time.time() - now} seconds to scrape all event data")

    df = pd.DataFrame(events) 
    fights_df = pd.concat([pd.DataFrame(x) for x in df['Fights']], keys=df.index).reset_index(level=1, drop=True)
    df = df.drop(columns='Fights').join(fights_df)
    df.to_csv("csv/ufc_events.csv", index=False)
