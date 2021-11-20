#!/bin/bash

./bin/docker_compose.sh --profile core \
                        --profile services \
                        --profile utils \
                        --profile site \
                        pull $@
