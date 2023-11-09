#!/bin/bash

# ==== Color ====

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

cd ..
echo -e "$GREEN Stop all containers$NC"
docker compose -f docker-compose-primary-replica.yml down


# check primary-replica/copy1 and primary-replica/copy2 exist or not
# if exist, remove them

if [ -d "../db_volumes/primary-replica/copy1" ]; then
    echo -e "$RED Remove$NC old data from$RED primary-replica/copy1$NC"
    rm -r ../db_volumes/primary-replica/copy1
    # rmdir ../db_volumes/primary-replica/copy1 > /dev/null 2>&1
fi


echo -e "$GREEN Remove old data$NC"
rm -r db_volumes/primary-replica/*

echo -e "$GREEN Start all containers$NC"
docker compose -f docker-compose-primary-replica.yml up -d