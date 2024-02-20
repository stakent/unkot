#!/bin/bash

set -e
set -m

# source: https://misc.flogisoft.com/bash/tip_colors_and_formatting
GREEN='\e[32m'
RED='\e[31m'

PORT=8002
DEV_URL="http://127.0.0.1:${PORT}"

# run django development server with DEBUG=False
DJANGO_READ_DOT_ENV_FILE=True DJANGO_DEBUG=False ./manage.py runserver 0.0.0.0:${PORT} &


# make sure MailHog receiving emails from django app is runnig
if [  `ps a | grep MailHog | wc -l` == 1 ]; then
	./MailHog_linux_amd64 &
fi

# django tests
dropdb --if-exists test_unkot_dev
./manage.py test --no-input --keepdb

cp .envs/cypress/devel.json cypress.env.json
CYPRESS_baseUrl=${DEV_URL} ./node_modules/.bin/cypress run

echo -e "${GREEN}Done testing on devel"
