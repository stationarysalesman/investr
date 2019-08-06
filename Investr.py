import requests
import time
import re
import xml.etree.ElementTree as ET
import datetime
import matplotlib.pyplot as plt
import numpy as np
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

    plt.show()
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
    return

# literally fuck you python I can't believe you make me do this every time
if __name__ == "__main__":
    main()
