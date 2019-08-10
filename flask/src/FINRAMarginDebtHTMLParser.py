from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from datetime import date
import datetime
import re
import copy

search = 'Debit Balances in Customers\' Securities Margin Accounts'
month_dict = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sept': '09', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
def dict_from_tuple(tups):
    d = dict()
    for item in tups:
        d[item[0]] = item[1]
    return d

class FINRAMarginDebtHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self) 
        self.collect_date = False
        self.collect_margin_debt = False
        self.entries = dict() 
        self.holder = None # placeholder
    def handle_starttag(self, tag, attrs):
        d = dict_from_tuple(attrs)
        try:
            if tag == 'td' and d['data-th'] == 'Month/Year':
                self.collect_date = True
               
            elif tag == 'td' and d['data-th'] == search:
                self.collect_margin_debt = True
        except KeyError:
            return

    def handle_data(self, data):
        if self.collect_date:
            try:
                mo,yr = re.split('-', data.encode('ascii'))
                month = int(month_dict[mo])
                year = int('20' + str(yr))
                # Stop collecting data if it's too old
                if year < date.today().year - 1:
                    self.collect_date = False
                    self.holder = None 
                else:
                    self.holder =  datetime.date(year, month, 15)
                    self.collect_date = False
            except UnicodeEncodeError:
                self.collect_date = False

        elif self.collect_margin_debt and self.holder:
            try:
                self.entries[self.holder] = int(data.replace(',', '')) # margin debt in $millions
                self.collect_margin_debt = False
                self.holder = None
            except ValueError:
                self.collect_margin_debt = False
                self.holder = None


    def handle_endtag(self, tag):
        return


    def get_margin_debt(self):
        return copy.deepcopy(self.entries)



