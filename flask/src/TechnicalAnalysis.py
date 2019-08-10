import requests
import numpy as np
import json
from DJIAHTMLParser import DJIAHTMLParser

def GetDJIAStonks():
    key = 'I0yZMg8jBWJ2b3czdNFo5mwIBSHIydSzM2oTOWhMpHzo7V6jdhKkrIZ8cLqa' # api key
    parser2 = DJIAHTMLParser()
    url = 'https://www.cnbc.com/dow-30/'
    r = requests.get(url)
    parser2.feed(r.text)
    djia_indexes = parser2.get_indexes()
# NOTE: The free API is limited to 250 requests per day, so don't test with 
# all the requests every time!
    stonks = []
# Get the actual stock trading data from the API
    chunks = [djia_indexes[i:i+5] for i in xrange(0, len(djia_indexes), 5)]
    print('chunks:')
    print(chunks)
    for elems in chunks:
        idxs_lst = ','.join(elems)
        print('will request:')
        print(idxs_lst)
        realtime_request_url = 'https://api.worldtradingdata.com/api/v1/stock'
        payload = {'symbol': idxs_lst, 'api_token':key}
        r = requests.get(realtime_request_url, params=payload)
        stock_json = json.loads(r.text)
        for item in stock_json['data']:
            d = dict()
            d['Symbol'] = item['symbol']
            d['Name'] = item['name']
            d['Price'] = item['price']
            d['OpeningPrice'] = item['price_open']
            d['ChangeUSD'] = item['day_change']
            d['ChangePCT'] = item['change_pct']
            d['PreviousClose'] = item['close_yesterday']
            d['MarketCap'] = item['market_cap']
            stonks.append(d)
        break

    sorted_stonks = sorted(stonks, key = lambda s: s['Symbol'])
    sorted_symbols = [stonk['Symbol'] for stonk in sorted_stonks]
    sorted_prices = [stonk['Price'] for stonk in sorted_stonks]
    d = {'sorted_symbols': sorted_symbols, 'sorted_prices': sorted_prices, 'stonks': sorted_stonks}
    return json.dumps(d)

