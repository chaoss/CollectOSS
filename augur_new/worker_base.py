
import os
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as s


from db_models import *
from config import AugurConfig
from oauth_key_manager import OauthKeyManager





#TODO: setup github headers in a method here.
#Encapsulate data for celery task worker api


#TODO: Test sql methods
class TaskSession(s.orm.Session):

    #ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

    def __init__(self,logger,config={},platform='github'):
        self.logger = logger
        
        current_dir = os.getcwd()

        self.root_augur_dir = ''.join(current_dir.partition("augur/")[:2])
        self.__init_config(self.root_augur_dir)
        
        DB_STR = f'postgresql://{self.config["user_database"]}:{self.config["password_database"]}@{self.config["host_database"]}:{self.config["port_database"]}/{self.config["name_database"]}'

        self.config.update(config)
        self.platform = platform
        
        #print(f"path = {str(ROOT_AUGUR_DIR) + "augur.config.json"}")
        

        self.__engine = s.create_engine(DB_STR)

        self.__oauths = OauthKeyManager(self.config,self.__engine,self.logger)

        super().__init__(self.__engine)

    def __init_config(self, root_augur_dir):
        #Load config.
        self.augur_config = AugurConfig(self.root_augur_dir)
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
            return self.__oauths.get_key()
        except:
            self.logger.error("No access token in queue!")
            return None

    
    def execute_sql(self, sql_text):
        connection = self.__engine.connect()

        return connection.execute(sql_text)
    
    def insert_data(self, data, table, natural_keys):

        self.logger.info(f"Length of data to insert: {len(data)}")
        self.logger.info(type(data))

        if type(data) != list:
            self.logger.info("Data must be a list")
            return

        if type(data[0]) != dict:
            self.logger.info("Must be list of dicts")
            return

        table_stmt = insert(table)
        for value in data:
            insert_stmt = table_stmt.values(value)
            insert_stmt = insert_stmt.on_conflict_do_update(
                index_elements=natural_keys, set_=dict(value))
            result = self.execute_sql(insert_stmt)

