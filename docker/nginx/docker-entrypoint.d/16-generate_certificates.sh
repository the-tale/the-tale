
#!/bin/sh

if [ ! -z $TT_GENERATE_CERTIFICATES];
then
    # exit if certificates generation does not required
    exit 0
fi

for tt_server in $TT_SERVERS
do
    certs_dir=/etc/nginx/certificates/$tt_server

    if [ ! -d $certs_dir ];
    then
        mkdir -p $certs_dir

        subject="/O=the-tale/CN=$domain"

        openssl req \
                -nodes \
                -x509 \
                -newkey rsa:4096 \
                -keyout "$certs_dir/privkey.pem" \
                -out "$certs_dir/fullcert.pem" \
                -days 3650 \
                -subj "$subject"
    fi
done
