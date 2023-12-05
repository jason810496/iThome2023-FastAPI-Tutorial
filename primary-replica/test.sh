#!/bin/bash

# ==== Color ====
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "$GREEN Load environment variables$NC"
source ./primary-replica/db.env
user=$POSTGRES_USER
db=$POSTGRES_DB


# wait until primary is ready using `pg_isready`
while ! docker exec -it primary bash -c "pg_isready -U $user -d $db"; do
    echo -e "$RED Wait until primary is ready$NC"
    sleep 1
done

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"

# wait until replica is ready using `pg_isready`
while ! docker exec -it replica bash -c "pg_isready -U $user -d $db"; do
    echo -e "$RED Wait until replica is ready$NC"
    sleep 1
done

echo -e "$GREEN List all tables in replica$NC"
docker exec -it replica bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN Add new table in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c 'CREATE TABLE test (id int);'"
sleep 1

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"
sleep 1

echo -e "$GREEN List all tables in replica$NC"
docker exec -it replica bash -c "psql -U $user -d $db -c '\dt'"
sleep 1

echo -e "$GREEN Add new table in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c 'CREATE TABLE test2 (id int);'"
sleep 1

echo -e "$GREEN List all tables in replica$NC"
docker exec -it replica bash -c "psql -U $user -d $db -c '\dt'"
sleep 1

echo -e "$RED Remove$NC test2 table in primary"
docker exec -it primary bash -c "psql -U $user -d $db -c 'DROP TABLE test2;'"

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN List all tables in replica$NC"
docker exec -it replica bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$RED Remove$NC test table in primary"
docker exec -it primary bash -c "psql -U $user -d $db -c 'DROP TABLE test;'"

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN List all tables in replica$NC"
docker exec -it replica bash -c "psql -U $user -d $db -c '\dt'"

