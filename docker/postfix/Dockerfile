FROM debian:bullseye-20211115

RUN apt-get update

RUN apt-get install -y locales && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

RUN apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y postfix

ENV LANG="en_US.utf8" \
    PATH="$PATH:/postfix-bin"

COPY ./requirements.txt /root/requirements.txt

RUN pip3 install -r /root/requirements.txt

COPY ./templates /postfix-config-templates
COPY ./bin /postfix-bin

CMD ["postfix", "start-fg"]

ENTRYPOINT ["entrypoint.sh"]
