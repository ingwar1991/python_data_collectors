#!/bin/bash

celery -A app.collectors.worker worker --loglevel=info
