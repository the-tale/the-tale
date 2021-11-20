#!/bin/bash

./bin/docker_compose.sh up -d
./bin/docker_compose.sh --profile services up -d

./bin/docker_compose.sh run utils-site tt_django game_create_world
./bin/docker_compose.sh run utils-site tt_django accounts_create_superuser
./bin/docker_compose.sh run utils-site tt_django portal_postupdate_operations

./bin/docker_compose.sh run utils-site-generate-static
