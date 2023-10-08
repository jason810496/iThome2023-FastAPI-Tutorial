
testing : 


deployment & details :
    - CORS :

web socket :
[pub sub pattern](https://notfalse.net/11/pub-sub-pattern)
[scaling-websockets-with-pub-sub](https://medium.com/@nandagopal05/scaling-websockets-with-pub-sub-using-python-redis-fastapi-b16392ffe291)

streaming : images / video / audio


redis : 
[redis py github](https://github.com/redis/redis-py)
> `aioredis` has been intergrated into `redis-py` since `v3.5.0`

[use redis](https://blog.csdn.net/wgPython/article/details/107668521)
    - [redis client setup example](https://github.com/tiangolo/fastapi/issues/1694)

[redis developer : fastapi example](https://github.com/redis-developer/fastapi-redis-tutorial/blob/master/app/main.py)

(partition) :

database sharding :



mongo :

[fastapi mongo crud](https://github.com/mongodb-developer/pymongo-fastapi-crud/blob/main/routes.py)
    - [db setup](https://github.com/mongodb-developer/pymongo-fastapi-crud/blob/main/main.py)
[fastapi mongo example](https://testdriven.io/blog/fastapi-mongo/)
[mongo image](https://hub.docker.com/_/mongo)
[mongo sharding](https://medium.com/hobo-engineer/%E7%AD%86%E8%A8%98-%E5%AF%A6%E4%BD%9C%E5%88%86%E6%95%A3%E5%BC%8F%E8%A8%88%E5%88%86%E7%B3%BB%E7%B5%B1-%E4%BA%8C-replica-set-in-container-5759b1b4cd5)


primary / replication architecture : 

- DB Level 

[video tutorial](https://www.youtube.com/watch?v=zxxzcpvCa6o&ab_channel=%E6%B2%88%E5%BC%98%E5%93%B2)
[postgresql note : master slave](https://github.com/twtrubiks/postgresql-note/tree/main/pg-master-slave)
[postgresql replication](https://editor.leonh.space/2023/postgresql-replication/)

[mysql : master slave](hhttps://medium.com/dean-lin/%E6%89%8B%E6%8A%8A%E6%89%8B%E5%B8%B6%E4%BD%A0%E5%AF%A6%E4%BD%9C-mysql-master-slave-replication-16d0a0fa1d04)

- Backend Level 
[example setup](https://itecnote.com/tecnote/python-read-slave-read-write-master-setup/)
[flask sqlalchemy example](https://techspot.zzzeek.org/files/2012/sqlalchemy_multiple_dbs.py)