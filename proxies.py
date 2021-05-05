import requests
from bs4 import BeautifulSoup

# Initialize proxy list with IP and port
proxy_list = []

# Get proxies from proxy table with Beautiful Soup 
def get_proxy():
    r = requests.get('https://free-proxy-list.net/') 
    soup = BeautifulSoup(r.text, 'lxml')
    proxy_table = soup.find(id='proxylisttable')
    # Insert each IP + port into proxies list
    for row in proxy_table.tbody.find_all('tr'):
        ip = row.find_all('td')[0].text
        port = row.find_all('td')[1].text
        proxy = "{ip}:{port}".format(ip=ip, port=port)
        proxy_list.append(proxy)
        


