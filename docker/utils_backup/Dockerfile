FROM the-tale/postgresql:latest

ENTRYPOINT ["entrypoint.sh"]

RUN apt-get update && apt-get install -y awscli

RUN mkdir -p /backups

COPY ./bin/* /usr/bin/
