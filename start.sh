#!/bin/bash
app="the-pattern-api"
network_name='redis_cluster_net'
docker build -t ${app} .
docker run -d -p 8080:8181 --rm --name=${app} --net $network_name -v $PWD:/app ${app}
