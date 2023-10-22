#!/bin/bash

# ==== Color ====

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# check primary-replica/copy1 and primary-replica/copy2 exist or not
# if exist, remove them

if [ -d "../db_volumes/primary-replica/copy1" ]; then
    echo -e "$RED Remove$NC old data from$RED primary-replica/copy1$NC"
    rm -r ../db_volumes/primary-replica/copy1
    # rmdir ../db_volumes/primary-replica/copy1 > /dev/null 2>&1
fi

if [ -d "../db_volumes/primary-replica/copy2" ]; then
    echo -e "$RED Remove$NC old data from$RED primary-replica/copy2$NC"
    rm -r ../db_volumes/primary-replica/copy2
    # rmdir ../db_volumes/primary-replica/copy2 > /dev/null 2>&1
fi



# Stop all containers before copy data
echo -e "$GREEN Restart all containers$NC"
docker restart primary replica1 replica2
sleep 2

# ==== Primary ====
user=postgresql_user
pass="'postgresql_password'"
db=postgresql_db

# Check dababase primary_db exist or not
echo -e "$GREEN Check database $db exist or not$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN Check users exist or not$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\du'"

# Add Replication User
repuser=repluser
reppass="'replpass'"

# Check replication user exist or not
echo -e "$GREEN Check replication user exist or not$NC"
exist=$(docker exec -it primary bash -c "psql -U $user -d $db -c '\du'" | grep $repuser | cut -d' ' -f 2)

# if does not exist, add replication user
if [ "$exist" != "$repuser" ]; then
    echo -e "$GREEN Add Replication User$NC"
    docker exec -it primary bash -c "psql -U $user -d $db -c \"CREATE ROLE $repuser WITH LOGIN REPLICATION PASSWORD $reppass;\""
    sleep 1
else
    echo -e "$GREEN Replication User exist$NC"
fi

# Allow replication connections from replica1 and replica2
echo -e "$GREEN Allow replication connections from replica1 and replica2$NC"
docker exec -it primary bash -c "echo 'host replication $repuser 172.22.0.101/32 md5' >> /var/lib/postgresql/data/pg_hba.conf"
docker exec -it primary bash -c "echo 'host replication $repuser 172.22.0.102/32 md5' >> /var/lib/postgresql/data/pg_hba.conf"

# Copy .postgresql.conf to /var/lib/postgresql/data/postgresql.conf
docker cp postgresql.conf primary:/var/lib/postgresql/data/postgresql.conf

# Restart primary
echo -e "$GREEN Restart primary$NC"
docker restart primary
sleep 1

# ==== Replica ====

# # check primary-replica/copy1 and primary-replica/copy2 exist or not
# # if exist, remove them

# if [ -d "../db_volumes/primary-replica/copy1" ]; then
#     echo -e "$RED Remove$NC old data from$RED primary-replica/copy1$NC"
#     rm -r ../db_volumes/primary-replica/copy1
#     # rmdir ../db_volumes/primary-replica/copy1 > /dev/null 2>&1
# fi

# if [ -d "../db_volumes/primary-replica/copy2" ]; then
#     echo -e "$RED Remove$NC old data from$RED primary-replica/copy2$NC"
#     rm -r ../db_volumes/primary-replica/copy2
#     # rmdir ../db_volumes/primary-replica/copy2 > /dev/null 2>&1
# fi


echo -e " Run$GREEN pg_basebackup$NC on$GREEN replica1$NC"
sleep 1
docker exec -it replica1 bash -c "pg_basebackup -R -D /var/lib/postgresql/primary_copy -Fp -Xs -v -P -h primary -p 5432 -U $repuser"
sleep 1

echo -e " Run$GREEN pg_basebackup$NC on$GREEN replica2$NC"
sleep 1
docker exec -it replica2 bash -c "pg_basebackup -R -D /var/lib/postgresql/primary_copy -Fp -Xs -v -P -h primary -p 5432 -U $repuser"

# Stop all containers before copy data
docker stop primary replica1 replica2

# Remove old data from replica1 and replica2
# Copy data from primary to replica1 and replica2

echo -e "Remove old data from$RED replica1$NC"
rm -r ../db_volumes/primary-replica/replica1/*
echo -e "$GREEN Copy$NC data from primary to$GREEN replica1$NC"
cp -r ../db_volumes/primary-replica/copy1/* ../db_volumes/primary-replica/replica1/

echo -e "Remove old data from$RED replica2$NC"
rm -r ../db_volumes/primary-replica/replica2/*
echo -e "$GREEN Copy$NC data from primary to$GREEN replica2$NC"
cp -r ../db_volumes/primary-replica/copy2/* ../db_volumes/primary-replica/replica2/

# Start all containers
docker start primary replica1 replica2