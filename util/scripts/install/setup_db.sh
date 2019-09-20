echo "If you need to install Postgres, the downloads can be found here: https://www.postgresql.org/download/"
installpostgreslocally="Would you like to use a pre-existing Postgres 10 or 11 installation to which you can install the Augur schema?"
installpostgresremotely="Would you like to use a pre-existing Postgres 10 or 11 installation to which someone else can install the Augur schema?"
postgresalreadyinstalled="Would you like to use a pre-existing Postgres 10 or 11 installation with the Augur schema already installed? "
SKIP="Skip this section"

select haveinstalledpostgres in "$installpostgreslocally" "$installpostgresremotely" "$postgresalreadyinstalled" "$SKIP"
do
  case $haveinstalledpostgres in
      $SKIP )
      echo "Skipping database configuration..."
      break
    ;;
    $installpostgreslocally )
        echo "After you have installed the Augur schema to your database, please return to this point in the installation."
        echo "Please enter the credentials for your database."
        enter_db_credentials
        break
      ;;
    $installpostgresremotely )
        echo "Once the Augur schema has been installed on to your database for you, please return to this point in the installation."
        echo "Please enter the credentials for your database."
        enter_db_credentials
        break
      ;;
    $postgresalreadyinstalled )
        echo "Please enter the credentials for your database."
        enter_db_credentials
        break
      ;;
  esac
done
