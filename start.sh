#!/bin/bash

cd docker || exit

COLLECTORS_CONTAINER_NAME='data_collectors_collectors'
FRONT_CONTAINER_NAME='data_collectors_front'
MONGO_CONTAINER_NAME='data_collectors_mongo'
REDIS_CONTAINER_NAME='data_collectors_redis'
WORKER1_CONTAINER_NAME='data_collectors_worker1'
WORKER2_CONTAINER_NAME='data_collectors_worker2'
WORKER3_CONTAINER_NAME='data_collectors_worker3'

COLOR_RED='\033[31m'
COLOR_GREEN='\033[32m'
COLOR_YELLOW='\033[33m'
COLOR_RESET='\033[0m'

detach=''
runTests=0
stopContainers=0

toCollectorsBash=0
toDbBash=0
toFrontBash=0
toRedisBash=0
toWorker1Bash=0
toWorker2Bash=0

if [ -n "$1" ] 
then
    if [ "$1" = "-b" ] 
    then
        if [ "$2" = "c" ]
        then
            toCollectorsBash=1
        elif [ "$2" = "d" ]
        then
            toDbBash=1
        elif [ "$2" = "f" ]
        then
            toFrontBash=1
        elif [ "$2" = "r" ]
        then
            toRedisBash=1
        elif [ "$2" = "w1" ]
        then
            toWorker1Bash=1
        elif [ "$2" = "w2" ]
        then
            toWorker2Bash=1
        elif [ "$2" = "w3" ]
        then
            toWorker3Bash=1
        fi
    elif [ "$1" = "-d" ] 
    then
        detach="-d"
    elif [ "$1" = "-t" ] 
    then
        detach="-d"
        runTests=1
    elif [ "$1" = "-s" ] 
    then
        detach="-d"
        stopContainers=1
    else
        echo -e "Usage: ./start {param} \n \
Parameters: \n \
    -d - run containers & detach \n \
    -b {DESTINATION}- go to container bash, where DESTINATION: \n \
        c - go to collectors container bash \n \
        f - go to front container bash \n \
        d - go to mongo container bash \n \
        r - go to redis container bash \n \
        w1 - go to worker1 container bash \n \
        w2 - go to worker2 container bash \n \
    -t - run containers, then run tests & stop on success, on error go to collectors container bash \n \
    -s - stop containers & remove volumes"
        exit
    fi
fi

if [ "$stopContainers" -eq 1 ] 
then
    echo -e "${COLOR_YELLOW}***Stopping containers***${COLOR_RESET}"
    docker compose down -v

    exit 0
fi

if [ "$toCollectorsBash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to collectors container bash***${COLOR_RESET}"
    docker compose exec "${COLLECTORS_CONTAINER_NAME}" bash

    exit 0
fi

if [ "$toFrontBash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to front container bash***${COLOR_RESET}"
    docker compose exec "${FRONT_CONTAINER_NAME}" bash

    exit 0
fi

if [ "$toDbBash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to mongo container bash***${COLOR_RESET}"
    docker compose exec "${MONGO_CONTAINER_NAME}" bash

    exit 0
fi

if [ "$toRedisBash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to redis container bash***${COLOR_RESET}"
    docker compose exec "${REDIS_CONTAINER_NAME}" bash

    exit 0
fi

if [ "$toWorker1Bash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to worker1 container bash***${COLOR_RESET}"
    docker compose exec "${WORKER1_CONTAINER_NAME}" bash

    exit 0
fi

if [ "$toWorker2Bash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to worker2 container bash***${COLOR_RESET}"
    docker compose exec "${WORKER2_CONTAINER_NAME}" bash

    exit 0
fi

if [ "$toWorker3Bash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to worker3 container bash***${COLOR_RESET}"
    docker compose exec "${WORKER3_CONTAINER_NAME}" bash

    exit 0
fi

echo -e "${COLOR_YELLOW}***Starting containers***${COLOR_RESET}"
if ! docker compose up $detach
then
    echo -e "${COLOR_RED}Failed to start containers.${COLOR_RESET}"
    exit 1
fi

if [ "$runTests" -eq 1 ] 
then
    echo -e "${COLOR_YELLOW}***Preparing for tests***${COLOR_RESET}"

    echo "Waiting for container to start..."
    until docker ps --filter "name=$COLLECTORS_CONTAINER_NAME" --filter "status=running" | grep -q "$COLLECTORS_CONTAINER_NAME"; do
        echo "Container is not ready yet, waiting..."
        sleep 2
    done

    echo "Running PY tests..."
    
    if docker compose exec "$COLLECTORS_CONTAINER_NAME" ./runTests.sh
    then
        echo -e "${COLOR_GREEN}Tests passed successfully!${COLOR_RESET}"
        
        # Stop the containers if tests passed
        stopContainers=1
    else
        echo -e "${COLOR_RED}Tests failed. Container will remain running.${COLOR_RESET}"
        # go to collectors container if tests failed
        toCollectorsBash=1
    fi
fi

if [ "$toCollectorsBash" -eq 1 ]
then
    echo -e "${COLOR_YELLOW}***Going to collectors container bash***${COLOR_RESET}"
    docker compose exec "${COLLECTORS_CONTAINER_NAME}" bash
fi

if [ "$stopContainers" -eq 1 ] 
then
    echo -e "${COLOR_YELLOW}***Stopping containers***${COLOR_RESET}"
    docker compose down -v
fi
