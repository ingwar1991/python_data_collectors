#!/bin/bash

# Stop DB test is any test failed
pytest -v tests/test_mongo.py --maxfail=1

# Process the rest tests normally 
pytest -v tests/ --ignore=tests/test_db.py
