#!/bin/bash

clear

uwsgi --http :80 --wsgi-file server.py