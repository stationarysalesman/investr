import requests
import numpy as np
import json
import re
from DJIAHTMLParser import DJIAHTMLParser
from FINRAMarginDebtHTMLParser import FINRAMarginDebtHTMLParser

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

    sorted_stonks = sorted(stonks, key = lambda s: s['Symbol'])
    sorted_symbols = [stonk['Symbol'] for stonk in sorted_stonks]
    sorted_changes = [stonk['ChangePCT'] for stonk in sorted_stonks]
    d = {'sorted_symbols': sorted_symbols, 'sorted_changes': sorted_changes, 'stonks': sorted_stonks}
    return json.dumps(d)

def load_vix_data():
    """Load the most recent VIX data from cboe.com"""
    url = 'http://www.cboe.com/publish/scheduledtask/mktdata/datahouse/vixcurrent.csv'
    r = requests.get(url)
    csv_text = r.text
    entries = re.split('\n', csv_text)
    entries_ascii = [x.encode('ascii') for x in entries] # Unicode -> ASCII
    entries_stripped = [x.strip() for x in entries_ascii] # remove trailing \r
    matrix = entries_stripped[2:-2] # ignore copyright text (i.e. fuck the police), header, and end
    dates = []
    vix_opens = []
    vix_highs = []
    vix_lows = []
    vix_closes = []
    for i in matrix:
        s = re.split(',', i)
        dates.append(s[0])
        vix_opens.append(s[1])
        vix_highs.append(s[2])
        vix_lows.append(s[3])
        vix_closes.append(s[4])
    return dates, vix_opens, vix_highs, vix_lows, vix_closes


def compute_ema_helper(data, output, n, alpha, i):
    """Iterative helper functin for compute_ema"""
    # base case (i starts at n-1)
    output[i] = np.mean(data[0:n])
    limit = len(data) - 1 
    i += 1
    while (i <= limit):
        output[i] =  output[i-1] + alpha * (data[i] - output[i-1]) 
        i += 1
    return


def compute_ema(data, n):
    """Compute the n day exponential moving average of stock data"""
    alpha = 2 / float(n + 1) # a reasonable weighting metric
    i = n-1 
    output = np.zeros(len(data))
    compute_ema_helper(data, output, n, alpha, i)
    return output


def compute_macd(data):
    """Compute the moving average convergent/divergent line for any stock, index, or mutual fund. 
    
    @param data: a 1D numpy array of prices
    @param n: number of data points in a single averaging step (i.e. an n-day moving average)
    @return output: the macd line with the same length as data (the first n-1 entries are 0)
    
    We will use the 12-day and 26-day exponential moving averages for our calculations."""
    
    macd_26 = compute_ema(data, 26)
    macd_12 = compute_ema(data, 12)

    # For calculations we need to strip off the zero values
    macd_26_stripped = macd_26[25:]
    macd_12_stripped = macd_12[25:] # consistency
    macd = macd_12_stripped - macd_26_stripped
    macd_signal = compute_ema(macd, 9)
    macd_signal_stripped = macd_signal[8:] 
    macd_stripped = macd[8:]

    histogram = macd_stripped - macd_signal_stripped
    return macd_26_stripped, macd_12_stripped, macd, histogram 

def GetVixMACD():
   # Compute the MACD for the VIX
    vix_dates, vix_opens, vix_highs, vix_lows, vix_closes = load_vix_data()
    vix_closes_float = [float(x) for x in vix_closes]
    vix_macd_26, vix_macd_12, vix_macd, vix_histogram = compute_macd(vix_closes_float)
    cut = len(vix_dates) - len(vix_histogram)
    cut2 = len(vix_macd_26) - len(vix_histogram)
    new_dates = vix_dates[cut:]
    new_vix = vix_closes_float[cut:]
    new_macd_26 = vix_macd_26[cut2:]
    new_macd_12 = vix_macd_12[cut2:]
    d = {'dates': new_dates, 'vix': list(new_vix), 'macd_26': list(new_macd_26), \
            'macd_12': list(new_macd_12), 'histogram': list(vix_histogram)}
    return json.dumps(d)


def GetMarginDebt():
    """Get margin debt data from the past year from FINRA"""
    parser = FINRAMarginDebtHTMLParser()
    url = 'https://www.finra.org/investors/margin-statistics'
    r = requests.get(url)
    parser.feed(r.text)
    margin_debt = parser.get_margin_debt()
    dates = sorted(margin_debt)
    debts = [margin_debt[x] for x in dates]
    dates_str = [str(x) for x in dates]
    d = {'dates': dates_str, 'debts': debts}
    return json.dumps(d)

