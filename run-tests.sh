#!/bin/sh

# print empty lines to mark start of new checks run
echo ""
echo ""
echo ""
echo "********************************************************"
echo ""

dropdb --if-exists test_unkot_dev
./manage.py test --no-input unkot
