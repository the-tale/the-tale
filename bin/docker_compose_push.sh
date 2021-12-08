#!/bin/bash

source ./bin/defaults.env

docker compose -f ./docker/docker-compose.build.yml \
               --profile core \
               --profile services \
               --profile utils \
               --profile site \
               --profile tasks \
               --profile tasks-manager \
               push $@
