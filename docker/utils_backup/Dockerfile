ARG TT_BASE_IMAGE_VERSION

FROM the-tale/core-postgresql:$TT_BASE_IMAGE_VERSION

ENTRYPOINT ["entrypoint.sh"]

RUN apt-get update && apt-get install -y awscli

RUN mkdir -p /backups

COPY ./bin/* /usr/bin/
