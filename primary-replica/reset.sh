#!/bin/bash

# ==== Color ====

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

cd ..
echo -e "$GREEN Stop all containers$NC"
docker compose -f docker-compose-primary-replica.yml down

echo -e "$GREEN Remove old data$NC"
rm -r db_volumes/primary-replica/*

echo -e "$GREEN Start all containers$NC"
docker compose -f docker-compose-primary-replica.yml up -d
