#!/bin/bash
# Run unittests
python -m unittest discover --start-directory ./test/ --pattern "Test*.py"
