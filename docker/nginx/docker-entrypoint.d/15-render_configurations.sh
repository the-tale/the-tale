#!/bin/sh

for tt_server in $TT_SERVERS
do
    template=/nginx-config-templates/$tt_server.conf.j2
    nginx_config=/etc/nginx/conf.d/$tt_server.conf

    jinja2 --strict $template /root/nginx_config.json > $nginx_config
done
