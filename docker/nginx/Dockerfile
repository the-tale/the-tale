FROM nginx:1.21.3

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install --upgrade pip

COPY ./requirements.txt /root/requirements.txt

RUN pip3 install -r /root/requirements.txt

RUN rm -f /etc/nginx/conf.d/default.conf

RUN mkdir -p /etc/nginx/certificates

COPY ./docker-entrypoint.d /docker-entrypoint.d

COPY ./templates /nginx-config-templates
