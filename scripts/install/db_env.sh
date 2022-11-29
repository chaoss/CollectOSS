  echo "Enter the database credentials to your empty database"
  read -p "Database: " db_name
  read -p "User: " db_user
  read -s -p "Password: " password
  echo
  read -p "Host: " host
  read -p "Port: " port
  export AUGUR_DB=postgresql+psycopg2://$db_user:$password@$host:$port/$db_name
