import requests
import xml.etree.ElementTree as ET
import datetime
import numpy as np
import json
from datetime import date


def GetDate():
    now = date.today()
    now_t = now.timetuple()
    year = str(now_t[0])
    month = str(now_t[1])
    day = str(now_t[2])
    return year, month, day

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
    return json.dumps(d)


