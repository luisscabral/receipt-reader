#!/bin/bash
app="receipt-reader"
docker build -t ${app}
docker run -d -p 8080:80 \
    --name=${app} \
    -v $PWD: /receipt_reader ${app}  