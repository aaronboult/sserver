#!/bin/bash

clear

# Set working directory to www/ folder and start server
cd ./www/

uwsgi --http :80 --wsgi-file server.py