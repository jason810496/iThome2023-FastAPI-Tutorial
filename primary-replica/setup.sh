#!/bin/bash

# ==== Color ====
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Stop all containers before copy data
echo -e "$GREEN Restart all containers$NC"
docker restart primary replica 
sleep 2

echo -e "$GREEN Load environment variables$NC"
source ./primary-replica/db.env
user=$POSTGRES_USER
pass="'$POSTGRES_PASSWORD'"
db=$POSTGRES_DB
repuser=$REPLICA_USER
reppass="'$REPLICA_PASSWORD'"


echo -e "$GREEN Wait until primary is ready$NC"
while ! docker exec -it primary bash -c "pg_isready -U $user -d $db"; do
    echo -e "$RED Wait until primary is ready$NC"
    sleep 1
done

echo -e "$GREEN Wait until replica is ready$NC"
while ! docker exec -it replica bash -c "pg_isready -U $user -d $db"; do
    echo -e "$RED Wait until replica is ready$NC"
    sleep 1
done

# Check dababase primary_db exist or not
echo -e "$GREEN Check database $db exist or not$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\dt'"

echo -e "$GREEN Check users exist or not$NC"
docker exec -it primary bash -c "psql -U $user -d $db -c '\du'"

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

# Allow replication connections from replica
echo -e "$GREEN Allow replication connections from replica$NC"
docker exec -it primary bash -c "echo 'host replication $repuser 172.22.0.101/32 md5' >> /var/lib/postgresql/data/pg_hba.conf"
# Copy .postgresql.conf to /var/lib/postgresql/data/postgresql.conf
docker cp ./primary-replica/postgresql.conf primary:/var/lib/postgresql/data/postgresql.conf

# Restart primary
echo -e "$GREEN Restart primary$NC"
docker restart primary
sleep 1

# ==== Replica ====
echo -e " Run$GREEN pg_basebackup$NC on$GREEN replica$NC"
sleep 1
docker exec -it replica bash -c "pg_basebackup -R -D /var/lib/postgresql/primary_copy -Fp -Xs -v -P -h primary -p 5432 -U $repuser"
sleep 1

# Stop all containers before copy data
docker stop primary replica

echo -e "Remove old data from$RED replica$NC"
rm -r ./db_volumes/primary-replica/replica/*
echo -e "$GREEN Copy$NC data from primary to$GREEN replica$NC"
cp -r ./db_volumes/primary-replica/copy1/* ./db_volumes/primary-replica/replica/


docker start primary replica