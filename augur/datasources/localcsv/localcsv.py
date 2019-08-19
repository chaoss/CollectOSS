#SPDX-License-Identifier: MIT
"""
Loads small included datasets
"""

import pandas as pd
import tldextract
from urllib.parse import urlparse
from augur.util import get_data_path
# end imports
# (don't remove the above line, it's for a script)

class LocalCSV(object):
    """
    Reads local CSV files
    """
    def __init__(self):
        return


    def classify_emails(self, email_series):
        """
        Sends a series of emails to the classifier method

        :param email_series: series of given emails
        """
        name_gender = pd.read_csv(get_data_path('name_gender.csv'), index_col=0)
        companies = pd.read_csv(get_data_path('companies.csv'), index_col=['website'])
    
        def classifier(email):
            """
            Classifies what the emails associates with, based on its suffix (.edu, .com, .net, etc.)

            :param email: desired email to be classified
            """
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
