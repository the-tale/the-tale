
#!/bin/sh

defaults_dir=/default_certificates

for tt_server in $TT_SERVERS
do
    certs_dir=/etc/nginx/certificates/$tt_server

    if [ ! -d $certs_dir ];
    then
        cp -r $defaults_dir $certs_dir
    fi
done
