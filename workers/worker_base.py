
from workers.worker_persistance import *
from augur import db_models
from workers.oauth_key_manager import *

#TODO: setup github headers in a method here.
#Encapsulate data for celery task worker api


#TODO: This opens the config and create the db string

class TaskSession(sqlalchemy.orm.Session):

    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self,logger,db_str,config={},platform='github'):
        self.logger = logger
        self.config = config
        self.platform = platform
        
        #print(f"path = {str(ROOT_AUGUR_DIR) + "augur.config.json"}")
        self._oauths = OauthKeyManager(str(ROOT_AUGUR_DIR) + "augur.config.json")

        self.engine = create_engine(db_str)

        super.__init__(self.engine)
    
    @property
    def access_token(self):
        try:
            return self._oauths.get_key()
        except:
            self.logger.error("No access token in queue!")
            return None
    


    