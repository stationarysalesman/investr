import requests
import time
import re
import xml.etree.ElementTree as ET
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
import json
from datetime import date
from FederalFundsRateHTMLParser import FederalFundsRateHTMLParser
from DJIAHTMLParser import DJIAHTMLParser


def get_date():
    now = date.today()
    now_t = now.timetuple()
    year = str(now_t[0])
    month = str(now_t[1])
    day = str(now_t[2])
    return year, month, day


def get_datestr():
    now = date.today()
    now_t = now.timetuple()
    year = now_t[0]
    month = now_t[1]
    day = now_t[2]
    return str(year) + str(month).zfill(2) + str(day).zfill(2) 


def get_corporate_bond_spread():
    year, month, day = get_date()
    last_year = str(int(year) - 1)
    date_begin = last_year + '-' + month + '-' + day
    date_today = year + '-' + month + '-' + day
    corporate_spread_url = 'https://fred.stlouisfed.org/graph/fredgraph.csv?bgcolor=%23e1e9f0&chart_type=line&drp=0&fo=open%20sans&graph_bgcolor=%23ffffff&height=450&mode=fred&recession_bars=on&txtcolor=%23444444&ts=12&tts=12&width=1168&nt=0&thu=0&trc=0&show_legend=yes&show_axis_titles=yes&show_tooltip=yes&id=BAA10Y&scale=left&cosd=' + date_begin + '&coed=' + date_today + '&line_color=%234572a7&link_values=false&line_style=solid&mark_type=none&mw=3&lw=2&ost=-99999&oet=99999&mma=0&fml=a&fq=Daily&fam=avg&fgst=lin&fgsnd=2009-06-01&line_index=1&transformation=lin&vintage_date=2019-08-06&revision_date=2019-08-06&nd=1986-01-02'
    r = requests.get(corporate_spread_url)
    csv_text = r.text
    entries = re.split('\n', csv_text)
    
    # Let's just look at the last 30 days or so
    desired_entries = entries[-31:-1] # last entry is the final newline?
    entry_dates = []
    entry_rates = []
    for entry in desired_entries:
        current_date, rate = re.split(',', entry)
        if rate == '.': # No data for this day
            continue
        entry_dates.append(current_date)
        entry_rates.append(rate)
    return entry_dates, entry_rates 


def get_fed_funds_rates():
    post_url = 'https://apps.newyorkfed.org/markets/autorates/fed-funds-search-result-page'
    post_data = dict()
    # As of 2019/08/06, NY Fed requires MM/DD/YYYY format for the date range
    # NOTE: The Federal Funds rate is NOT published on weekends and holidays, so 
    # the dates returned from the database may not reflect the requested dates!
    year, month, day = get_date() 
    post_data['txtDate1'] = month + '/' + day + '/' + str(int(year)-1)
    post_data['txtDate2'] = month + '/' + day + '/' + str(int(year))

    r = requests.post(post_url, post_data)
    parser = FederalFundsRateHTMLParser()
    parser.feed(r.text)
    fed_funds_rates = parser.get_rates()
    return fed_funds_rates


def get_todays_stonks():
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
        idxs_lst = ','.join(elems[:2]) 
        realtime_request_url = 'https://api.worldtradingdata.com/api/v1/stock'
        payload = {'symbol': idxs_lst, 'api_token':key}
        r = requests.get(realtime_request_url, params=payload)
        stock_json = json.loads(r.text)
        for item in stock_json['data']:
            d = dict()
            d['Symbol'] = item['symbol']
            d['Name'] = item['name']
            d['Price'] = item['price']
            d['Opening Price'] = item['price_open']
            d['Change (USD)'] = item['day_change']
            d['Change (%)'] = item['change_pct']
            d['Previous Close'] = item['close_yesterday']
            d['Market Cap'] = item['market_cap']
            stonks.append(d)
        break 
    return stonks 


def export_stonks_to_csv(stonks):
    """Write a list of dicts out to csv"""
    with open('stonks' + get_datestr() + '.csv', 'w') as csvfile:
        fieldnames = ['Name', 'Symbol', 'Price', 'Opening Price', 'Previous Close', 'Change (USD)', 'Change (%)', 'Market Cap']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for stonk in stonks:
            writer.writerow(stonk)
    return


def get_fed_xml_entry(url):
    """Returns the most recent Federal entry data from an XML tree found at url (must be a Federal yield curve/bill rate url)
    
    @param url: the url of the XML file
    @return entry_date: the date of the entry in the Fed database
    @return entry: the most recent <entry> element in the XML tree"""
    # Submit the GET request
    r = requests.get(url)

    # Parse the response
    # Based on inspecting the XML, we will just assume the last 'entry' tag 
    # has the most recent entry
    root = ET.fromstring(r.text)
    entry = root[-1]
    entry_data = entry[6][0][1].text
    entry_date = datetime.datetime.strptime(entry_data, '%Y-%m-%dT%H:%M:%S') # format the Fed uses
    return entry_date, entry


def get_treasury_yields():    
    year, month, day = get_date()
    # Construct HTTP GET request
    base_url = 'https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=month(NEW_DATE)%20eq%20'
    base_url += str(month).zfill(2)
    base_url += '%20and%20year(NEW_DATE)%20eq%20'
    base_url += str(year)
    entry_date, entry = get_fed_xml_entry(base_url)
    yields = [float(x.text) for x in entry[6][0][2:14]]
    return yields, entry_date


def get_treasury_bill_rates():
    year, month, day = get_date()
    # Construct HTTP GET request
    base_url = 'https://data.treasury.gov/feed.svc/DailyTreasuryBillRateData?$filter=month(INDEX_DATE)%20eq%20'
    base_url += str(month).zfill(2)
    base_url += '%20and%20year(INDEX_DATE)%20eq%20'
    base_url += str(year)


    entry_date, entry = get_fed_xml_entry(base_url)
    
    # The Fed releases both the bank discount and coupon equivalent bill rates
    # We will use the coupon equivalent so that the rates can be compared to Treasury bond yields
    yields = [float(x.text) for x in entry[6][0][2:12:2]]
    return yields, entry_date


def main():
    print('-------------------------- here we are getting the -----------------------------')
    print('------------------------------- fInAnCiAl DaTa ---------------------------------')
    print('------------------------------------- ;) ---------------------------------------')
    
    # A key indicator of the market is the spread between the 3 month and 10 year bond yield
    yields, yield_date = get_treasury_yields()
    plt.figure(1)
    plt.xticks(np.arange(12), ('1 mo', '2 mo', '3 mo', '6 mo', '1 yr', '2 yr', '3 yr', '5 yr', '7 yr', '10 yr', '20 yr', '30 yr'))
    plt.plot(np.arange(12), yields)
    title_str = 'Treasury Yield Curve (' + str(yield_date) + ')'
    plt.title(title_str)
    plt.axis([0, 12, min(yields) * 0.9, max(yields) * 1.1])
    plt.xlabel('Bond Maturity Date')
    plt.ylabel('Treasury Yield Rate (%)')
    spread_3mo10yr = yields[9] - yields[2]
    print('3 month/10 year Treasury bond yield spread: %1.2f%%' % spread_3mo10yr)
    
    # Another key indicator is the money market (e.g. Federal Treasury bill rates) 
    bill_rates, bill_rates_entry_date = get_treasury_bill_rates() 
    plt.figure(2)
    plt.xticks(np.arange(5), ('1 mo', '2 mo', '3 mo', '6 mo', '1 yr'))
    plt.plot(np.arange(5), bill_rates)
    title_str_2 = 'Treasury Bill Rates (' + str(bill_rates_entry_date) + ')'
    plt.title(title_str_2)
    plt.axis([0, 5, min(bill_rates) * 0.9 , max(bill_rates) * 1.1])
    plt.xlabel('Bill Loan Period')
    plt.ylabel('Treasury Bill Rate (%)')

    monotonic = True
    r = bill_rates[0]
    for rate in bill_rates[1:]:
        if rate < r:
            monotonic = False
        r = rate

    reporter = None
    if monotonic:
        reporter = 'Normal'
    else:
        reporter = 'Abnormal'

    print('Money Market Indicator: %s' % reporter)


    # Another indicator is the spread between the 10 yr and 30 yr (long-term bond market)
    # Investors buying up 30 yr bonds, depressing their yield, indicates that they want to 
    # lock in high interest rates now (before the anticipated drop)
    spread_10yr30yr = yields[-1] - yields[-3]
    spread_20yr30yr = yields[-1] - yields[-2]
    print('20 year/30 year Treasury bond yield spread: %1.2f%%' % spread_20yr30yr)
    print('10 year/30 year Treasury bond yield spread: %1.2f%%' % spread_10yr30yr)

    # Several other long-term market indicators include:
    # - the yield on a 10 year bond ( > 10% means sell)
    # - the interest rate ( > 10% means sell)
    # - whether we have reached our expected return from the stock market already (10%)
    # - institutions' tendency to sell after realizing 10% gains on the stock market
    # Recessions often occur when the interest on a long-term security (like the 10 yr bond) rises
    # and especially when it rises beyond 10%
    # So, we want to know what the 10 year bond yield is specifically
    print('10 year Treasury bond yield: %1.2f%%' % yields[-3])


    # Another indicator is the spread between corporate bonds (Moody's BAA, just above "Junk bonds") 
    # and the Treasury 10 year bill
    entry_dates, entry_rates = get_corporate_bond_spread()
    entry_dates_str = [x.encode('ascii') for x in entry_dates]
    entry_rates_str = [x.encode('ascii') for x in entry_rates]
    entry_rates_float = [float(x) for x in entry_rates_str]
    entries = len(entry_dates_str)
    xs = np.arange(entries)
    plt.figure(3)
    plt.xticks(xs[::2], tuple(entry_dates_str[::2]))
    plt.plot(xs, entry_rates_float)
    title_str_3 = 'Moody\'s Corporate Bond Yield Relative to the 10 Year Treasury Note'
    plt.title(title_str_3)
    plt.axis([0, entries, min(entry_rates_float) * 0.9 , max(entry_rates_float) * 1.1])
    plt.xlabel('Date')
    plt.ylabel('Yield Spread (%)')
    

    # Let's determine how long the spread has been increasing, if at all
    idx = len(entry_rates_str) - 1
    while (idx > 0 and entry_rates_float[idx] > entry_rates_float[idx-1]):
        idx -= 1
    print('Corporate bond yield spread (relative to 10 year Treasury note) has been rising for %d days (since %s)' % (len(entry_rates_str) - 1 - idx, entry_dates_str[idx]))
    print('Most recent data published on %s' % entry_dates_str[-1])

    # The federal funds rate (the interest rate banks charge other banks for short term loans) 
    # is a bellwether of the direction in which the Fed wants to take the economy.
    # Historically, the federal funds rate has increased leading up to a recession, and 
    # turns around during the peak of the recession, declining after. 

    # The Federal Reserve Bank of New York provides historical effective federal funds rates
    fed_funds_rates = get_fed_funds_rates() 
    fed_funds_dates_lst = sorted(fed_funds_rates)
    fed_funds_rates_lst = [fed_funds_rates[x] for x in fed_funds_dates_lst] 
    fed_funds_dates_str = [str(x) for x in fed_funds_dates_lst]
    funds_entries = len(fed_funds_rates_lst)
    xs_funds = np.arange(funds_entries)
    plt.figure(4)
    plt.subplot(211)
    plt.xticks(xs_funds[::30], fed_funds_dates_str[::30]) 
    plt.plot(xs_funds, fed_funds_rates_lst)
    title_str_4 = 'Federal Funds Rates (past year)'
    plt.title(title_str_4)
    plt.axis([0, funds_entries, 0, 25])
    plt.xlabel('Date')
    plt.ylabel('Federal Funds Rate (%)')

    # Also make a subplot of the past 30 days
    plt.subplot(212)
    new_xs = fed_funds_dates_str[-30:] 
    plt.xticks(np.arange(30)[::3], new_xs[::3])
    plt.plot(np.arange(30), fed_funds_rates_lst[-30:])
    title_str_5 = 'Federal Funds Rates (past month)'
    plt.title(title_str_5)
    plt.axis([0, 30, min(fed_funds_rates_lst) * 0.95, max(fed_funds_rates_lst) * 1.05])
    plt.xlabel('Date')
    plt.ylabel('Federal Funds Rate (%)')



    ################### Technical Analysis ###################################

    stonks = get_todays_stonks()
    
    # Visualize the data
    plt.figure(5)
    entries = len(stonks)
    stonk_symbols = [d['Symbol'] for d in stonks]
    stonk_day_changes = [float(d['Change (%)']) for d in stonks]
    plt.xticks(np.arange(entries), stonk_symbols)
    plt.axhline(y=0, color='r', linestyle='-')
    plt.plot(np.arange(entries), stonk_day_changes)
    title_str_6 = 'Dow Jones Industrial Average Percent Change'
    plt.title(title_str_6)
    plt.axis([0, 30, min(stonk_day_changes) - 1, max(stonk_day_changes) + 1])
    plt.xlabel('Ticker Symbol')
    plt.ylabel('Day Change (%)')

    # Make a table and save to CSV for reporting
    export_stonks_to_csv(stonks) 



    # Show all the plots
    plt.show()
# literally fuck you python I can't believe you make me do this every time
if __name__ == "__main__":
    main()
