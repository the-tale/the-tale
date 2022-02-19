#!/bin/bash

if [ "$TT_ENV" != "tests" ] && [ "$TT_ENV" != "stage" ]  && [ "$TT_ENV" != "prod" ];
then
    echo "TT_ENV variable has wrong value: " $TT_ENV
    exit 1
fi;

echo "ENVIRONMENT: " $TT_ENV
echo "VERSION: " $TT_VERSION
echo "RELEASE VERSION" $TT_RELEASE_VERSION
