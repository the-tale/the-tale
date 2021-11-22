#!/bin/bash

tt_prepair_user () {
    echo "create user and database for '$1' with permissions: $3"
    psql -q -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
          CREATE USER $1 WITH PASSWORD '$2' $3;
EOSQL
}

tt_prepair_user $TT_DB_MANAGER_USER $TT_DB_MANAGER_PASSWORD "NOSUPERUSER CREATEROLE NOINHERIT LOGIN NOREPLICATION CREATEDB"
