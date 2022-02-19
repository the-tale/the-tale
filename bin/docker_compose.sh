#!/bin/bash

# load redefined variables, for example, in production environment
if [ -f ./bin/variables.env ];
then
    source ./bin/variables.env
fi;

source ./bin/defaults.env

./bin/check_and_info.sh

docker compose -f ./docker/docker-compose.templates.yml \
               -f ./docker/docker-compose.base.yml \
               -f ./docker/docker-compose.$TT_ENV.yml \
               $@
