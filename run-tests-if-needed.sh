#!/bin/sh

# find . -name '*.py' | entr ./run-tests.sh
find . -type f \( -name "*.py" -o -name "*.html" \) | entr ./run-tests.sh
