#!/bin/bash

source ./bin/defaults.env

export DOCKER_BUILDKIT=1

docker-compose -f ./docker/docker-compose.build.yml \
               --profile core \
               --profile services \
               --profile utils \
               --profile site \
               build $@
