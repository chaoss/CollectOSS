#SPDX-License-Identifier: MIT
"""
Loads small included datasets
"""
import pandas as pd
import tldextract
from urllib.parse import urlparse
from .util import get_data_path
# end imports
# (don't remove the above line, it's for a script)

class LocalCSV(object):
    
    def __init__(self):
        return

    name_gender = pd.read_csv(get_data_path('name_gender.csv'), index_col=0)
    companies = pd.read_csv(get_data_path('companies.csv'), index_col=['website'])

    def classify_emails(self, email_series):
    
        def classifier(email):
            if email is None:
                return 'Unknown'
            ext = tldextract.extract(email)
            domain = '{}.{}'.format(ext.domain, ext.suffix)
            if ext.suffix == 'edu':
                return 'Academic Institutions'
            if domain in self.companies.index:
                return self.companies['company'][domain]
            else:
                return 'Unknown'
        
        return email_series.map(classifier)
