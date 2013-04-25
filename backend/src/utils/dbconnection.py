import conf
import pymongo
from redis import Redis

def clear_mongo():
    if not conf.test:
        raise Exception("clear_mongo is called for not test configuration")
    db = mongo()
    client = db.connection
    client.drop_database(db.name)
    client.close()

def clear_redis():
    if not conf.test:
        raise Exception("clear_redis is called for not test configuration")
    client = redis()
    client.flushdb()

# return mongo collection
def mongo_collection(name):
    db = mongo()
    return db[name]

def mongo_ensure_indexes(*classes):
    for c in classes:
        c.ensure_indexes()

def mongo():
    c = conf.database
    # TODO configure to use replica set
    # db = pymongo.MongoReplicaSetClient(c.hosts, w = c.w, j = c.j, replicaSet='replica')
    client = pymongo.MongoClient(c.hosts, w = c.w, j = c.j)
    dbname = c.name if not conf.test else c.test_name
    return client[dbname]


def redis():
    c = conf.redis
    db = c.db if not conf.test else c.test_db
    client = Redis(host = c.host, port = c.port, db=db)
    return client
