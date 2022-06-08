
from workers.worker_persistance import *
from augur import db_models
from augur.config import AugurConfig
from workers.oauth_key_manager import *


#TODO: setup github headers in a method here.
#Encapsulate data for celery task worker api


#TODO: This opens the config and create the db string

class TaskSession(sqlalchemy.orm.Session):

    ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self,logger,config={},platform='github'):
        self.logger = logger
        
        self.root_augur_dir = ROOT_AUGUR_DIR
        self.__init_config(self.root_augur_dir)
        
        DB_STR = f'postgresql://{self.config["user_database"]}:{self.config["password_database"]}@{self.config["host_database"]}:{self.config["port_database"]}/{self.config["name_database"]}'

        self.config.update(config)
        self.platform = platform
        
        #print(f"path = {str(ROOT_AUGUR_DIR) + "augur.config.json"}")
        

        self._engine = create_engine(DB_STR)

        self._oauths = OauthKeyManager(self.config,db_str=DB_STR)

        super.__init__(self._engine)

    def __init_config(self, root_augur_dir):
        #Load config.
        self.augur_config = AugurConfig(self.root_augur_dir,config)
        self.config = {
            'host': self.augur_config.get_value('Server', 'host')
        }
        self.config.update(self.augur_config.get_section("Logging"))

        self.config.update({
            'capture_output': False,
            'host_database': self.augur_config.get_value('Database', 'host'),
            'port_database': self.augur_config.get_value('Database', 'port'),
            'user_database': self.augur_config.get_value('Database', 'user'),
            'name_database': self.augur_config.get_value('Database', 'name'),
            'password_database': self.augur_config.get_value('Database', 'password'),
            'key_database' : self.augur_config.get_value('Database', 'key')
        })

        print(self.config)

    
    @property
    def access_token(self):
        try:
            return self._oauths.get_key()
        except:
            self.logger.error("No access token in queue!")
            return None
    


    