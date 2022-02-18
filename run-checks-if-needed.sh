#!/bin/sh

find . -name '*.py' | entr ./run-checks.sh
