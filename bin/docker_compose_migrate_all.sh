#!/bin/sh

tt_services=`./bin/docker_compose.sh ps --services | grep tt_ | grep -v tt_service`

for tt_service in $tt_services
do
    echo "migrate service" $tt_service
    ./bin/docker_compose.sh run --entrypoint tt_django $tt_service migrate
done

./bin/docker_compose.sh run --entrypoint tt_django the_tale migrate
