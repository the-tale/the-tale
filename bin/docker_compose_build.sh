#!/bin/bash

source ./bin/defaults.env

./bin/check_and_info.sh

export DOCKER_BUILDKIT=1

docker compose -f ./docker/docker-compose.build.yml \
               --profile core \
               --profile services \
               --profile utils \
               --profile site \
               build $@
