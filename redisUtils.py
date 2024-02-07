import redis

RedisDB = 0


class RedisUtils:

    def __init__(self):
        pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=RedisDB, decode_responses=True)
        self.redis = redis.Redis(connection_pool=pool)

    def __getRedisConn(self):
        return self.redis

    def __close(self):
        pass

    def close(self):
        pass

    def pipeline(self):
        return self.__getRedisConn().pipeline(transaction=False)

    def tick(self):
        return self.__getRedisConn().ping()

    # 操作string
    def set(self, key, value):
        rd = self.__getRedisConn()
        return rd.set(key, value)

    def get(self, key):
        rd = self.__getRedisConn()
        return rd.get(key)

    def exist(self, key):
        self.__getRedisConn().exists(key)

    def keydel(self, *args):
        return self.__getRedisConn().delete(*args)

    def kpersist(self, *args):
        return self.__getRedisConn().persist(*args)

    def kpttl(self, *args):
        return self.__getRedisConn().pttl(*args)

    # next lines kylinz create
    # seconds:设置过期时间
    def setex(self, key, seconds, value):
        return self.__getRedisConn().setex(key, seconds, value)

    # 操作hash
    def hmset(self, name, mapping):
        # if expireTime:
        #     return self.__getRedisConn().expire(name, expireTime)
        # else:
        return self.__getRedisConn().hmset(name, mapping)

    def hmget(self, name, *args):
        return self.__getRedisConn().hmget(name, *args)

    def hgetvals(self, name):
        return self.__getRedisConn().hvals(name)

    def hexists(self, name, field):
        return self.__getRedisConn().hexists(name, field)

    def hgetall(self, name):
        return self.__getRedisConn().hgetall(name)

    # 操作list
    def lpush(self, name, *values):
        return self.__getRedisConn().lpush(name, *values)

    def lpop(self, name):
        return self.__getRedisConn().lpop(name)

    def ltrim(self, name, start, end):  # 保留指定范围list
        return self.__getRedisConn().ltrim(name, start, end)

    def llen(self, key):
        return self.__getRedisConn().llen(key)

    def lfindValue(self, name, value):
        nameLst = self._getNameLst(name)
        if value in nameLst:
            return 1
        return -1

    # 操作set
    def sadd(self, name, *values):
        return self.__getRedisConn().sadd(name, *values)

    def srem(self, name, *values):
        return self.__getRedisConn().srem(name, *values)

    def getSetLength(self, name):
        return self.__getRedisConn().scard(name)

    # kylinz add get all set
    def sgetmembers(self, name):
        return self.__getRedisConn().smembers(name)

    def setWarn(self, typeName, name, **kwargs):
        # 如果获取不到name的time字段才插入，为了解决list的重复问题，如果用set的话，清除数据的时候有点麻烦
        if not self.hexists(name, "time"):
            self.hmset(name, **kwargs)
            self.lpush(typeName, name)

    # kylinz add
    # handel oder set
    def zRangeByScore(self, name, min, max):
        return self.__getRedisConn().zrangebyscore(name, min, max)

    def zRemRangeByScore(self, name, min, max):
        return self.__getRedisConn().zremrangebyscore(name, min, max)

    def pipeSetWarn(self, pipe=None, typeName=None, name=None, **kwargs):
        pipe.hmset(name, kwargs)
        pipe.zadd(typeName, {name: int(kwargs['time'])})

    def _getNameLst(self, name):
        return self.__getRedisConn().zrange(name, 0, -1)

    def _getNameLen(self, name):
        return self.__getRedisConn().llen(name)

    # 数据存储
    def save_front(self):
        return self.__getRedisConn().save()

    def save_background(self):
        return self.__getRedisConn().bgsave()

    def subscribe(self, *channels):
        return self.__getRedisConn().pubsub().subscribe(*channels)

    def unsubscribe(self, *channels):
        return self.__getRedisConn().pubsub().unsubscribe(*channels)

    def publish(self, channel, message):
        return self.__getRedisConn().publish(channel, message)

    def listen(self):
        return self.__getRedisConn().pubsub().listen()

    def getKey(self, pattern):
        return self.__getRedisConn().keys(pattern)

    def flushAll(self):
        return self.__getRedisConn().flushdb()

    def expire(self, key, ex_time):
        return self.__getRedisConn().expire(key, ex_time)

    def getRedisClient(self):
        return self.__getRedisConn()


def main():
    redisUtils = RedisUtils()
    deviceId = 'dfff0001'
    price = redisUtils.get('price:' + deviceId)
    if price is None:
        redisUtils.setex('price:' + deviceId, 30, 1.234)
    else:
        price = float(price.decode('utf-8'))


if __name__ == '__main__':
    main()

if __name__ != '__main__':
    RedisClient = RedisUtils()
