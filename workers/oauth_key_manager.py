from queue import Queue
import datetime
import httpx
import json
import sqlalchemy as s
import pandas as pd
import time


class OauthKeyManager():
    def __init__(self, config_file_path):

        print("Initializing Oauth key manager")

        self.fresh_key_cutoff = 0

        # make a connection to the database
        operations_schema = 'augur_operations'
        operations_db_conn = get_db_connection(
            config_file_path, operations_schema)

        # create a list of oauth keys
        config_key = get_oauth_key_from_config(config_file_path)
        oauth_keys = get_list_of_oauth_keys(operations_db_conn, config_key)

        fresh_keys_list = []
        depleted_keys_list = []

        # define httpx client for making requests to api        
        with httpx.Client() as client:

            # loop throuh each key in the list and get the rate_limit and seconds_to_reset
            # then add them either the fresh keys or depleted keys based on the rate_limit
            for oauth in oauth_keys:

                # gets the data for the key
                # key_data has a strucutre of
                """
                Data has this structure
                key_data = {
                    'oauth_id': <oauth_id>,
                    'access_token': <oauth_key,
                    'rate_limit': <requests_remaining>,
                    'seconds_to_reset': <seconds_till_rate_limit_is_replenished>
                }
                """
                key_data = get_oauth_key_data(client, oauth)

                # this makes sure that keys with bad credentials are not used
                if key_data is None:
                    continue

                
                if key_data["rate_limit"] >= self.fresh_key_cutoff:
                    # add key to the fresh keys list
                    fresh_keys_list.append(key_data)
                else:
                    # add it to the depleted keys list
                    depleted_keys_list.append(key_data)

        self.fresh_keys = Queue(maxsize=30)
        self.depleted_keys = []

        # sort the fresh keys by rate_limit from smallest to largeset so that the keys with the least requests get used first
        sorted_fresh_keys = sorted(
            fresh_keys_list, key=lambda k: k["rate_limit"])

        # add the keys to the queue
        for key in sorted_fresh_keys:
            self.fresh_keys.put(key)
        
        sorted_depleted_keys = sorted(
            depleted_keys_list, key=lambda k: k["seconds_to_reset"])

        for key in sorted_depleted_keys:
            self.depleted_keys.append(key)
    
    # mehtod to obtain a new key when one runs out
    def get_key(self):

        while self.fresh_keys.empty() is True:
            
            self.replenish_fresh_keys()

            if self.fresh_keys.empty() is False:
                break

            print("Sleeping for 60 seconds to wait for new keys")
            time.sleep(60)

        print(self.fresh_keys.queue)

        first_key = list(self.fresh_keys.queue)[0]

        return first_key

    # helper method to move a key from fresh to depleted
    def mark_as_depleted(self):
        
        # removes key from fresh key queue
        depleted_key = self.fresh_keys.get()

        # adds it to the depleted keys
        self.depleted_keys.append(depleted_key)

    # method that checks the depleted keys to see if they have been reset
    def replenish_fresh_keys(self):

        print("Checking for keys that are replenished now")

        with httpx.Client() as client:
            count = 0
            for key in self.depleted_keys:

                # get the data for the keys
                key_data = get_oauth_key_data(client, key)

                # if the key meets the rate limit cutoff then add it to the fresh keys queue and delelte it from the depleted keys list
                if key_data["rate_limit"] >= self.fresh_key_cutoff:
                    self.fresh_keys.put(key)
                    del key
                    count += 1

            print(f"Found {count} keys that were replenished")

################################################################################

# Helper functions relating to oauth keys

def get_oauth_key_from_config(config_file_path):

    with open(config_file_path, 'r') as f:
        return json.load(f)["Database"]["key"]


def get_list_of_oauth_keys(operations_db_conn, config_key):

    oauthSQL = s.sql.text(f"""
            SELECT * FROM worker_oauth WHERE access_token <> '{config_key}' and platform = 'github'
            """)

    oauth_keys_list = [{'oauth_id': 0, 'access_token': config_key}] + json.loads(
        pd.read_sql(oauthSQL, operations_db_conn, params={}).to_json(orient="records"))

    return oauth_keys_list


def get_oauth_key_data(client, oauth_key_data):

    rate_limit_header_key = "X-RateLimit-Remaining"
    rate_limit_reset_header_key = "X-RateLimit-Reset"
    url = "https://api.github.com/users/sgoggins"

    headers = {'Authorization': f'token {oauth_key_data["access_token"]}'}

    response = client.request(
        method="GET", url=url, headers=headers, timeout=180)

    data = response.json()

    try:
        if data["message"] == "Bad credentials":
            return None
    except KeyError:
        pass

    seconds_to_reset = (
        datetime.datetime.fromtimestamp(
            int(
                response.headers[rate_limit_reset_header_key])
        ) - datetime.datetime.now()
    ).total_seconds()

    key_data = {
        'oauth_id': oauth_key_data['oauth_id'],
        'access_token': oauth_key_data['access_token'],
        'rate_limit': int(response.headers[rate_limit_header_key]),
        'seconds_to_reset': seconds_to_reset
    }

    return key_data

################################################################################

# Helper functions relating to the database 

def get_db_conn_string(config_file_path):

    with open(config_file_path, 'r') as f:
        db_config = json.load(f)["Database"]

    DB_STR = f'postgresql://{db_config["user"]}:{db_config["password"]}@{db_config["host"]}:{db_config["port"]}/{db_config["name"]}'

    return DB_STR


def get_db_connection(config_file_path, schema):

    DB_STR = get_db_conn_string(config_file_path)

    db_conn = s.create_engine(DB_STR, poolclass=s.pool.NullPool,
                                connect_args={'options': f'-csearch_path={schema}'})

    return db_conn


################################################################################


# Main function to test program

def main():
    # url = "https://api.github.com/repos/chaoss/augur/issues/events?per_page=50&page=5"
    config = '../augur.config.json'

    key_manager = OauthKeyManager(config)

    my_key = key_manager.get_key()

    print(my_key)




if __name__ == '__main__':
    # This code won't run if this file is imported.
    main()
