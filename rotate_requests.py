import requests, time, random
from itertools import cycle
from fake_useragent import UserAgent
from proxies import *

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