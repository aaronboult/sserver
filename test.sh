#!/bin/bash
# Run unittests
cd ./sserver/
python -m unittest discover --start-directory ./test/ --pattern "Test*.py"
