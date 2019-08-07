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

class DJIAHTMLParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self) 
        self.CollectIndexName = False
        self.index_holder = [] # the list of indices currently on the DJIA 
    def handle_starttag(self, tag, attrs):
        d = dict_from_tuple(attrs)
        try:
            if tag == 'td' and d['data-field'] == 'symbol':
                self.CollectIndexName = True  

        except KeyError:
            return

    def handle_data(self, data):
        if self.CollectIndexName:
            self.index_holder.append(data.encode('ascii'))
            self.CollectIndexName = False


    def handle_endtag(self, tag):
        return


    def display(self):
        print(self.changes)


    def get_indexes(self):
        return copy.deepcopy(self.index_holder)



