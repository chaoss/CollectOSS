from queue import Queue
import datetime
import httpx
import json
import sqlalchemy as s
import pandas as pd


class OauthKeyManager():
    def __init__(self, config_file_path):

        rate_limit_header_key = "X-RateLimit-Remaining"
        rate_limit_reset_header_key = "X-RateLimit-Reset"

        operations_schema = 'augur_operations'

        operations_db_conn = get_db_connection(
            config_file_path, operations_schema)

        config_key = get_oauth_key_from_config(config_file_path)

        
        oauth_keys = get_list_of_oauth_keys(operations_db_conn, config_key)

        fresh_keys_list = []
        depleted_keys_list = []

        url = "https://api.github.com/users/sgoggins"
  
        with httpx.Client() as client:

            for oauth in oauth_keys:

                headers = {'Authorization': 'token %s' % oauth['access_token']}

                response = client.request(method="GET", url=url, headers=headers, timeout=180)

                data = response.json()
                
                try:
                    if data["message"] == "Bad credentials":
                        continue
                except KeyError:
                    pass

                seconds_to_reset = (
                    datetime.datetime.fromtimestamp(
                        int(
                            response.headers[rate_limit_reset_header_key])
                    ) - datetime.datetime.now()
                ).total_seconds()

                key_data = {
                    'oauth_id': oauth['oauth_id'],
                    'access_token': oauth['access_token'],
                    'rate_limit': int(response.headers[rate_limit_header_key]),
                    'seconds_to_reset': seconds_to_reset
                }

                if key_data["rate_limit"] >= 4800:
                    # add key to the fresh keys list
                    fresh_keys_list.append(key_data)
                else:
                    # add it to the depleted keys list
                    depleted_keys_list.append(key_data)

        self.fresh_keys = Queue(maxsize=30)
        self.depleted_keys = Queue(maxsize=30)

        sorted_fresh_keys = sorted(
            fresh_keys_list, key=lambda k: k["rate_limit"])

        for key in sorted_fresh_keys:
            self.fresh_keys.put(key)
        

        sorted_depleted_keys = sorted(
            depleted_keys_list, key=lambda k: k["seconds_to_reset"])

        for key in sorted_depleted_keys:
            self.depleted_keys.put(key)


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


# Main function to test program

def main():
    # url = "https://api.github.com/repos/chaoss/augur/issues/events?per_page=50&page=5"
    config = '../augur.config.json'

    key_manager = OauthKeyManager(config)




if __name__ == '__main__':
    # This code won't run if this file is imported.
    main()
