
import os
from sqlalchemy.dialects.postgresql import insert
import sqlalchemy as s


from augur_new import db_models 
from sqlalchemy.event import listen
from sqlalchemy.event import listens_for
from augur.config import AugurConfig
from augur_new.oauth_key_manager import OauthKeyManager


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
        

        self.engine = s.create_engine(DB_STR)

        self.__oauths = OauthKeyManager(self.config,self.engine,self.logger)

        super().__init__(self.engine)

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
        connection = self.engine.connect()

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

    #TODO: Bulk upsert
    
    def insert_bulk_data(self,data,table,natural_keys):
        self.logger.info(f"Length of data to insert: {len(data)}")
        self.logger.info(type(data))

        if type(data) != list:
            self.logger.info("Data must be a list")
            return

        if type(data[0]) != dict:
            self.logger.info("Must be list of dicts")
            return

        stmnt = insert(table).values(data)

        setDict = {}
        for key in data.keys:
            setDict[key] = getattr(stmnt.excluded,key)

        stmnt = stmnt.on_conflict_do_update(
            #This might need to change
            index_elements=natural_keys,
            
            #Columns to be updated
            set_ = setDict
        )

        self.execute(stmnt)


#Derek 
@s.event.listens_for(TaskSession, "connect", insert=True)
def set_search_path(dbapi_connection, connection_record):
    existing_autocommit = dbapi_connection.autocommit
    dbapi_connection.autocommit = True
    cursor = dbapi_connection.cursor()
    cursor.execute("SET SESSION search_path=public,augur_data,augur_operations,spdx")
    cursor.close()
    dbapi_connection.autocommit = existing_autocommit