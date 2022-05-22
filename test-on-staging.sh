#!/bin/bash

set -e
set -x

# source: https://misc.flogisoft.com/bash/tip_colors_and_formatting
GREEN='\e[32m'
RED='\e[31m'

STAGING_SSH='d@p7'
STAGING_REPO='/home/d/project/unkot/staging/unkot'

ssh $STAGING_SSH "\
	mkdir -p $STAGING_REPO; \
	cd $STAGING_REPO; \
	git init -bare . \
"


git push --follow-tags repo-staging


ssh $STAGING_SSH "\
	cd $STAGING_REPO; \
	git checkout -f staging \
"

rsync -r .envs ${STAGING_SSH}:${STAGING_REPO}

cp .envs/cypress/staging.json cypress.env.json 

ssh $STAGING_SSH "\
	cd $STAGING_REPO; \
	docker-compose -f local.yml up --force-recreate --build -d \
"

CYPRESS_baseUrl=http://192.168.0.200:8001 ./node_modules/.bin/cypress run

echo -e "${GREEN}Successfully done testing on staging ($STAGING_SSH)"
