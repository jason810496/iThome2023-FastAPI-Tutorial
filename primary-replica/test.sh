#!/bin/bash

# ==== Color ====

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

user=postgresql_user
db=postgresql_db

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN List all tables in replica1$NC"
docker exec -it replica1 bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN Add new table in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c 'CREATE TABLE test (id int);'"
sleep 1

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"
sleep 1

echo -e "$GREEN List all tables in replica1$NC"
docker exec -it replica1 bash -c "psql -U $user -d $db -c '\dt'"
sleep 1

echo -e "$GREEN List all tables in replica2$NC"
docker exec -it replica2 bash -c "psql -U $user -d $db -c '\dt'"
sleep 1

echo -e "$GREEN Add new table in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c 'CREATE TABLE test2 (id int);'"
sleep 1

echo -e "$GREEN List all tables in replica1$NC"
docker exec -it replica1 bash -c "psql -U $user -d $db -c '\dt'"
sleep 1

echo -e "$GREEN List all tables in replica2$NC"
docker exec -it replica2 bash -c "psql -U $user -d $db -c '\dt'"
sleep 1


echo -e "$RED Remove$NC test2 table in primary"
docker exec -it primary bash -c "psql -U $user -d $db -c 'DROP TABLE test2;'"

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN List all tables in replica1$NC"
docker exec -it replica1 bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN List all tables in replica2$NC"
docker exec -it replica2 bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$RED Remove$NC test table in primary"
docker exec -it primary bash -c "psql -U $user -d $db -c 'DROP TABLE test;'"

echo -e "$GREEN List all tables in primary$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"


