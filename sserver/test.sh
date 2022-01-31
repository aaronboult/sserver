#!/bin/bash

# Set working directory
cd /sserver/sserver/

# Run unittests
python -m unittest discover --start-directory ./test/ --pattern "Test*.py"
