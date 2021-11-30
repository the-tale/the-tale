#!/bin/sh

certs_dir=/default_certificates

mkdir -p $certs_dir

subject="/O=the-tale"

openssl req \
        -nodes \
        -x509 \
        -newkey rsa:4096 \
        -keyout "$certs_dir/privkey.pem" \
        -out "$certs_dir/fullcert.pem" \
        -days 3650 \
        -subj "$subject"
