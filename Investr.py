import requests
import time
import re
import xml.etree.ElementTree as ET
import datetime
import matplotlib.pyplot as plt
import numpy as np
from datetime import date


def get_treasury_yields():    
    # what day is it??

    now = date.today()
    now_t = now.timetuple()
    year = now_t[0]
    month = now_t[1]
    day = now_t[2]

    # Construct HTTP GET request
    base_url = 'https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=month(NEW_DATE)%20eq%20'

    # This thing is really fucky so we'll just build it manually...
    base_url += str(month).zfill(2)
    base_url += '%20and%20year(NEW_DATE)%20eq%20'
    base_url += str(year)

    # Submit the GET request
    r = requests.get(base_url)

    # Parse the response
    # Based on inspecting the XML, we will just assume the last 'entry' tag 
    # has the most recent entry
    root = ET.fromstring(r.text)
    entry = root[-1]
    entry_data = entry[6][0][1].text
    entry_date = datetime.datetime.strptime(entry_data, '%Y-%m-%dT%H:%M:%S') # format the Fed uses

    yields = [float(x.text) for x in entry[6][0][2:14]]


    return yields, entry_date

def main():
    print('-------------------------- here we are getting the -----------------------------')
    print('------------------------------- fInAnCiAl DaTa ---------------------------------')
    print('------------------------------------- ;) ---------------------------------------')
    yields, yield_date = get_treasury_yields()

    plt.figure(1)
    plt.xticks(np.arange(12), ('1 mo', '2 mo', '3 mo', '6 mo', '1 yr', '2 yr', '3 yr', '5 yr', '7 yr', '10 yr', '20 yr', '30 yr'))
    plt.plot(np.arange(12), yields)
    title_str = 'Treasury Yield Curve (' + str(yield_date) + ')'
    plt.title(title_str)
    plt.axis([0, 12, 0, max(yields) * 1.5])
    plt.xlabel('Bond Maturity Date')
    plt.ylabel('Treasury Yield Rate (%)')
    
    # A key indicator of the market is the spread between the 3 month and 10 year bond yield
    spread_3mo10yr = yields[9] - yields[2]
    print('3 month/10 year Treasury bond yield spread: %1.2f%%' % spread_3mo10yr)
    return

# literally fuck you python I can't believe you make me do this every time
if __name__ == "__main__":
    main()
