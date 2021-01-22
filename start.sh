#!/bin/bash
app="the-pattern-api"
network_name='redis_cluster_net'
docker build -t ${app} .
docker run -d --rm -p 85.10.241.154:8181:8181 --name=${app} --net $network_name ${app}
# docker run -d -p 8181:8181 \
#   --name=${app} --net $network_name\
#   -v $PWD:/app ${app}
