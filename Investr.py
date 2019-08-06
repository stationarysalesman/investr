import requests
import time
import re
import xml.etree.ElementTree as ET
import datetime
import matplotlib.pyplot as plt
import numpy as np
import csv
from datetime import date


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
    # what day is it??

    now = date.today()
    now_t = now.timetuple()
    year = now_t[0]
    month = now_t[1]
    day = now_t[2]

    # Construct HTTP GET request
    base_url = 'https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=month(NEW_DATE)%20eq%20'
    base_url += str(month).zfill(2)
    base_url += '%20and%20year(NEW_DATE)%20eq%20'
    base_url += str(year)
    entry_date, entry = get_fed_xml_entry(base_url)
    yields = [float(x.text) for x in entry[6][0][2:14]]
    return yields, entry_date


def get_treasury_bill_rates():
    # what day is it??

    now = date.today()
    now_t = now.timetuple()
    year = now_t[0]
    month = now_t[1]
    day = now_t[2]

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



    return bill_rates, entry_date
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

    # Actually plot the data?
    #plt.show()
    
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
    now = date.today()
    now_t = now.timetuple()
    year = str(now_t[0])
    month = str(now_t[1])
    day = str(now_t[2])
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
    
    # Plot? 
    #plt.show()

    # Let's determine how long the spread has been 
# literally fuck you python I can't believe you make me do this every time
if __name__ == "__main__":
    main()
