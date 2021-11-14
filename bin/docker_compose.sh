#!/bin/bash

source ./bin/defaults.env

if [ "$TT_ENV" != "tests" ] && [ "$TT_ENV" != "stage" ]  && [ "$TT_ENV" != "prod" ];
then
    echo "TT_ENV variable has wrong value: " $TT_ENV
    exit 1
fi;

DOCKER_BUILDKIT=1 docker-compose -f ./docker/docker-compose.base.yml -f ./docker/docker-compose.$TT_ENV.yml $@
