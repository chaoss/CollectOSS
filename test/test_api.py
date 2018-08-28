import os
import augur

augur_app = augur.Application(config_file="augur.config.json")
postman_api_key = augur_app.read_config("Postman", "apikey", "AUGUR_POSTMAN_API_KEY", "None")

os.system("newman run https://api.getpostman.com/collections/4566755-ec950b0b-a5e9-4fe3-b1a5-ad4f49c209f9?apikey={} -e https://api.getpostman.com/environments/4566755-2eb8f02c-642f-4f12-892f-d75f4c5faa24?apikey={} --color off | tee test/api-test.log".format(postman_api_key, postman_api_key))