#!/bin/bash

# ==== Color ====
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "$GREEN Stop all containers$NC"
docker compose -f docker-compose-primary-replica.yml down


if [ -d "./db_volumes/primary-replica/copy1" ]; then
    echo -e "$RED Remove$NC old data from$RED primary-replica/copy1$NC"
    rm -r ./db_volumes/primary-replica/copy1
fi


# echo -e "$GREEN Remove old data$NC"
# if [ -d "./db_volumes/primary-replica" ]; then
#     echo -e "$RED Remove$NC old data from$RED primary-replica$NC"
#     rm -r ./db_volumes/primary-replica
# fi

echo -e "$GREEN Start all containers$NC"
docker compose -f docker-compose-primary-replica.yml up -d
