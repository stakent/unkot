#!/bin/bash

set -e
# set -x

# start state: tested code on branch staging on x230

if [ -z "$1" ]
  then
    echo "Expected tag as first argument"
    echo "Existing tags:"
    git tag
    exit
fi


TAG=$1
# source: https://misc.flogisoft.com/bash/tip_colors_and_formatting
GREEN='\e[32m'
RED='\e[31m'

PRODUCTION_SSH='root@unkot.pl'
PRODUCTION_REPO='/root/project/unkot/prod'


git checkout main

git merge staging

git tag ${TAG}

git checkout production

git merge main

git push --follow-tags repo-production

ssh $PRODUCTION_SSH "\
        cd $PRODUCTION_REPO; \
	git checkout -f production; \
	docker-compose -f production.yml up --force-recreate --build -d \
"
