from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint
from datetime import date
import re
import copy
def dict_from_tuple(tups):
    d = dict()
    for item in tups:
        d[item[0]] = item[1]
    return d

class FederalFundsRateHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self) 
        self.CollectDate = False
        self.CollectRate = False
        self.dist_from_date = 0 # how far into the table we are
        self.rates = dict()
        self.date_holder = None # placeholder
    def handle_starttag(self, tag, attrs):
        d = dict_from_tuple(attrs)
        try:
            if tag == 'td' and d['class'] == 'dirColLTight':
                self.CollectDate = True  
                self.dist_from_date = 0

            elif tag == 'td' and d['class'] == 'dirColTight numData':
                self.dist_from_date += 1
                if self.dist_from_date == 2:
                    self.CollectRate = True
        except KeyError:
            return

    def handle_data(self, data):
        processed_data = data.replace(' ', '')
        processed_data = processed_data.replace('\r\n', '')
        if self.CollectDate:
            date_str = processed_data.encode('ascii')
            month,day,year = re.split('/', date_str) 
            self.date_holder = date(int(year), int(month), int(day))
            self.CollectDate = False
        elif self.CollectRate:
            self.rates[self.date_holder] = float(processed_data) 
            self.CollectRate = False
    def handle_endtag(self, tag):
        return


    def display(self):
        print(self.rates)


    def get_rates(self):
        return copy.deepcopy(self.rates)


