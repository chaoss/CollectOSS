#!bash

augur configure generate --db_name $AUGUR_DB_NAME --db_host $AUGUR_DB_HOST --db_port $AUGUR_DB_PORT --db_user $AUGUR_DB_USER --db_password $AUGUR_DB_PASSWORD --github_api_key $AUGUR_GITHUB_API_KEY --facade_repo_directory $AUGUR_FACADE_REPO_DIRECTORY

augur run --disable-housekeeper &
