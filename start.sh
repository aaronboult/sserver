#!/bin/bash

clear

# Set working directory to ./test_app/ folder and start server
cd ./test_app/

uwsgi --http :80 --wsgi-file server.py