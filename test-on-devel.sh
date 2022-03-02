#!/bin/bash

set -e

# source: https://misc.flogisoft.com/bash/tip_colors_and_formatting
GREEN='\e[32m'
RED='\e[31m'

DEV_URL='http://127.0.0.1:8001'

# django tests 
dropdb --if-exists test_unkot_dev
./manage.py test --no-input --keepdb

# cypress tests against devel server
cp .envs/cypress/devel.json cypress.env.json
./node_modules/.bin/cypress run

echo -e "${GREEN}Done testing on devel"
