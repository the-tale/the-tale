#!/bin/bash

# TODO: replace CREATEDB with NOCREATEDB for production

tt_prepair_service_database () {
    echo "create user and database for '$1'"
    psql -q -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
          CREATE USER $1 WITH PASSWORD '$1' NOSUPERUSER NOCREATEROLE NOINHERIT LOGIN NOREPLICATION CREATEDB;
    	  CREATE DATABASE $1 WITH OWNER $1;
EOSQL
}


for name in $TT_DATABASES
do
    tt_prepair_service_database "$name"
done
