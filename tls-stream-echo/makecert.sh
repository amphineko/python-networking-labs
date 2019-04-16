#!/usr/bin/env bash

openssl req -x509 \
    -newkey rsa:4096 \
    -keyout key.pem -out cert.pem -nodes \
    -subj "/CN=example.com" -days 365