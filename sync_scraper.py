import requests
import pandas as pd 
from bs4 import BeautifulSoup
from string import ascii_lowercase as alphabet
import time

# Initialize data storage
urls = []
fighter_urls = []

"""Synchronous method: ~21.60 seconds to get all fighter urls"""

def fetch_fighter_urls():
    for url in urls:
        # Get fighter-detail urls from each page
        page = requests.get(url)
        # Create Beautiful Soup object that takes HTML content and parser
        soup = BeautifulSoup(page.content, 'lxml')
        # Extract individual fighter urls into fighter_urls
        links = soup.select('a.b-link')
        hrefs = [l['href'] for l in links]
        unique_links = list(set(hrefs))
        fighter_urls.extend(unique_links)

def fetch_page_urls():
    """Get all alphabetical athlete list pages"""
    for ch in alphabet:
        url = f"http://ufcstats.com/statistics/fighters?char={ch}&page=all"
        urls.append(url)

if __name__ == '__main__':
    fetch_page_urls()
    
    t0 = time.time()
    fetch_fighter_urls()
    t1 = time.time()
    print(f"{t1-t0} seconds to finish")
    print(len(fighter_urls))
    # df = pd.DataFrame(fighter_urls)
    # df.to_csv('athlete_links.csv')


    
    

