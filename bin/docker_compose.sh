#!/bin/bash

# load redefined variables, for example, in production environment
if [ -f ./bin/variables.env ];
then
    source ./bin/variables.env
fi;

source ./bin/defaults.env

if [ "$TT_ENV" != "tests" ] && [ "$TT_ENV" != "stage" ]  && [ "$TT_ENV" != "prod" ];
then
    echo "TT_ENV variable has wrong value: " $TT_ENV
    exit 1
fi;

echo "ENVIRONMENT: " $TT_ENV
echo "VERSION: " $TT_VERSION
echo "RELEASE VERSION" $TT_RELEASE_VERSION

docker-compose -f ./docker/docker-compose.templates.yml \
               -f ./docker/docker-compose.base.yml \
               -f ./docker/docker-compose.$TT_ENV.yml \
               $@
