#!/bin/bash

clear

# Set Working Directory
cd /sserver/test_proj/

# Start server
uwsgi --http :80 --wsgi-file server.py --socket /tmp/__main__.sock --master --cache2 name=__main__,items=100 -storedelete --uid www-data --gid www-data --chmod-socket=666