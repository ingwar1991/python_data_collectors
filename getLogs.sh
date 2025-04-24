#!/bin/bash

cd docker || exit

COLLECTORS_CONTAINER_NAME='data_collectors_collectors'
FRONT_CONTAINER_NAME='data_collectors_front'
MONGO_CONTAINER_NAME='data_collectors_mongo'
REDIS_CONTAINER_NAME='data_collectors_redis'
WORKER1_CONTAINER_NAME='data_collectors_worker1'
WORKER2_CONTAINER_NAME='data_collectors_worker2'
WORKER3_CONTAINER_NAME='data_collectors_worker3'

CONTAINER_NAME=''
if [ -n "$1" ] 
then
    if [ "$1" = "c" ]
    then
        CONTAINER_NAME="${COLLECTORS_CONTAINER_NAME}"
    elif [ "$1" = "d" ]
    then
        CONTAINER_NAME="${MONGO_CONTAINER_NAME}"
    elif [ "$1" = "f" ]
    then
        CONTAINER_NAME="${FRONT_CONTAINER_NAME}"
    elif [ "$1" = "r" ]
    then
        CONTAINER_NAME="${REDIS_CONTAINER_NAME}"
    elif [ "$1" = "w1" ]
    then
        CONTAINER_NAME="${WORKER1_CONTAINER_NAME}"
    elif [ "$1" = "w2" ]
    then
        CONTAINER_NAME="${WORKER2_CONTAINER_NAME}"
    elif [ "$1" = "w3" ]
    then
        CONTAINER_NAME="${WORKER3_CONTAINER_NAME}"
    fi
else
    echo -e "Usage: ./getLogs {param} \n \
Parameters: \n \
    c - go to collectors container bash \n \
    f - go to front container bash \n \
    d - go to mongo container bash \n \
    r - go to redis container bash \n \
    w1 - go to worker1 container bash \n \
    w2 - go to worker2 container bash"
    exit
fi

container_id=$(docker compose ps -q "${CONTAINER_NAME}")
docker logs "${container_id}"
