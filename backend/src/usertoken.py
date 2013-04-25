import conf
import uuid
from utils.dbconnection import redis

class UserToken():
    _redis = redis()
    _hash_name = "usertoken:"
    _ttl = conf.user.token_ttl

    userid  = None
    tokenid = None

    def __str__(self):
        return "<%s:%s>" % (self.tokenid, self.userid)

    @staticmethod
    def new(userid, tokenid = None):
        token = UserToken()
        token.userid  = userid
        token.tokenid = tokenid or token._generate()
        token.save()
        return token

    @staticmethod
    def get(tokenid, update = True):
        token = UserToken()
        key_name = token._key_name(tokenid)
        value = token._redis.get(key_name)
        if value is None:
            return None

        if update:
            token._redis.expire(key_name, token._ttl)

        token.tokenid = tokenid
        token.userid = value

        return token


    def _pack(self):
        return self.userid

    def save(self):
        self._set(self.token, self._pack())

    def _generate(self):
        self.token = uuid.uuid4().hex
        return self.token

    def _key_name(self, token):
        return self._hash_name + token

    def _set(self, token, value):
        self._redis.setex(self._key_name(token), value, self._ttl)

