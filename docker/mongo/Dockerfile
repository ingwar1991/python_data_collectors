FROM mongo:noble
RUN apt-get update && \
    apt-get install -y vim gettext && \
    rm -rf /var/lib/apt/lists/*
ARG MONGO_DB_NAME
ARG MONGO_PORT
ARG MONGO_USER
ARG MONGO_USER_PASS
COPY template.js.tpl /docker-entrypoint-initdb.d/
RUN export MONGO_DB_NAME=${MONGO_DB_NAME} && \
    export MONGO_PORT=${MONGO_PORT} && \
    export MONGO_USER=${MONGO_USER} && \
    export MONGO_USER_PASS=${MONGO_USER_PASS} && \
    envsubst '${MONGO_DB_NAME} ${MONGO_USER} ${MONGO_USER_PASS}' < /docker-entrypoint-initdb.d/template.js.tpl > /docker-entrypoint-initdb.d/init.js && \
    chmod 644 /docker-entrypoint-initdb.d/init.js && \
    rm /docker-entrypoint-initdb.d/template.js.tpl
