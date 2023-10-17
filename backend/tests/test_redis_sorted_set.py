import redis

REDIS_URL = "redis://localhost:6379"

connection_pool = redis.ConnectionPool.from_url(REDIS_URL)

def test_create():
    rc = redis.Redis(connection_pool=connection_pool)

    rc.zadd( name="test_sorted_set", mapping={"a":1,"b":2,"c":3} )

    assert rc.zrange(name="test_sorted_set",start=0,end=-1) == [b'a', b'b', b'c']


def test_get_with_score():
    rc = redis.Redis(connection_pool=connection_pool)

    rc.zadd( name="test_sorted_set", mapping={"a":1,"b":2,"c":3} )

    assert rc.zrange(name="test_sorted_set",start=0,end=-1,withscores=True) == [(b'a', 1.0), (b'b', 2.0), (b'c', 3.0)]

def test_update_with_old_element():
    rc = redis.Redis(connection_pool=connection_pool)

    rc.zadd( name="test_sorted_set", mapping={"a2":1,"b2":2,"c2":3} ,nx=True )

    # assert rc.zrange(name="test_sorted_set",start=0,end=-1,withscores=True) == [(b'a', 2.0), (b'b', 4.0), (b'c', 6.0)]

