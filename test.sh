#!/bin/bash

# Set working directory
cd /sserver/sserver/

# Run unittests
python -m unittest discover --start-directory ./tests/ --pattern "Test*.py"
