import requests
import xml.etree.ElementTree as ET
import datetime
import numpy as np
import json
import re
import os
import pickle
from datetime import date
from FederalFundsRateHTMLParser import FederalFundsRateHTMLParser


def LoadFromCache(fname):
    j = None
    with open('./cache/'+fname, 'rb') as f:
        j = pickle.load(f)
    return j


def GetDate():
    now = date.today()
    now_t = now.timetuple()
    year = str(now_t[0])
    month = str(now_t[1])
    day = str(now_t[2])
    return year, month, day

def cache_datestr():
    y,m,d = GetDate()
    return y + m + d

def GetFedXMLEntry(url):
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


def GetTreasuryBillRates():
    year, month, day = GetDate()
    # Construct HTTP GET request
    base_url = 'https://data.treasury.gov/feed.svc/DailyTreasuryBillRateData?$filter=month(INDEX_DATE)%20eq%20'
    base_url += str(month).zfill(2)
    base_url += '%20and%20year(INDEX_DATE)%20eq%20'
    base_url += str(year)
    entry_date, entry = GetFedXMLEntry(base_url)
    # The Fed releases both the bank discount and coupon equivalent bill rates
    # We will use the coupon equivalent so that the rates can be compared to Treasury bond yields
    yields = [float(x.text) for x in entry[6][0][2:12:2]]
    d = {'date': str(entry_date), 'billrates': list(yields)}
    return json.dumps(d)


def GetTreasuryYields():    

    year, month, day = GetDate()
    # Construct HTTP GET request
    base_url = 'https://data.treasury.gov/feed.svc/DailyTreasuryYieldCurveRateData?$filter=month(NEW_DATE)%20eq%20'
    base_url += str(month).zfill(2)
    base_url += '%20and%20year(NEW_DATE)%20eq%20'
    base_url += str(year)
    entry_date, entry = GetFedXMLEntry(base_url)
    yields = [float(x.text) for x in entry[6][0][2:14]]
    d = {'date': str(entry_date), 'yields': list(yields)}
    j = json.dumps(d)
    return j

def GetFederalFundsRates():
    post_url = 'https://apps.newyorkfed.org/markets/autorates/fed-funds-search-result-page'
    post_data = dict()
    # As of 2019/08/06, NY Fed requires MM/DD/YYYY format for the date range
    # NOTE: The Federal Funds rate is NOT published on weekends and holidays, so 
    # the dates returned from the database may not reflect the requested dates!
    year, month, day = GetDate()
    post_data['txtDate1'] = month + '/' + day + '/' + str(int(year)-1)
    post_data['txtDate2'] = month + '/' + day + '/' + str(int(year))

    r = requests.post(post_url, post_data)
    parser = FederalFundsRateHTMLParser()
    parser.feed(r.text)
    fed_funds_rates = parser.get_rates()

    dates = sorted(fed_funds_rates)
    dates_str = [str(x) for x in dates]
    funds = [fed_funds_rates[x] for x in dates]
    d = {'dates': dates_str[-14:], 'federalfunds': funds[-14:]}
    return json.dumps(d)

def GetCorporateBondSpread():
    year, month, day = GetDate()
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

    d = {'dates': entry_dates, 'rates': entry_rates}
    return json.dumps(d)


