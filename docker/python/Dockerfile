FROM python:3.10
RUN apt-get update && apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install flask pymongo pyyaml python-dateutil requests pytest celery redis 
