#!/bin/bash

tt_prepair_service_database () {
    echo "create user and database for '$1' with permissions: $2"

    psql -q -v ON_ERROR_STOP=1 --user "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
        CREATE USER $1 WITH PASSWORD '$1' $2;
EOSQL

    psql -q -v ON_ERROR_STOP=1 --user "$POSTGRES_USER" --dbname "postgres" <<-EOSQL
        CREATE DATABASE $1 WITH OWNER $1;
EOSQL
}


export PGPASSWORD="$POSTGRES_PASSWORD"

echo "========================="
echo "Create services databases"
echo "========================="

for name in $TT_DATABASES
do
    permissions="NOSUPERUSER NOCREATEROLE NOINHERIT LOGIN NOREPLICATION"

    if [ "$TT_ENV" != "prod" ];
    then
        permissions="$permissions CREATEDB"
    fi;

    tt_prepair_service_database "$name" "$permissions"
done
