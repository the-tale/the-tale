#!/bin/sh

if [ -f /usr/bin/protoc ]; then
    echo "protobuf already installed"
    exit 0
fi

rm -rf /tmp/protobuf
mkdir /tmp/protobuf
wget https://github.com/google/protobuf/releases/download/v3.1.0/protoc-3.1.0-linux-x86_64.zip -O /tmp/protobuf/proto.zip
cd /tmp/protobuf && unzip proto.zip
cp /tmp/protobuf/bin/protoc /usr/bin
chmod 755 /usr/bin/protoc
