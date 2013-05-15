import conf
from bson.objectid import ObjectId

class Model(object):
    collection = None
    indexes = None

    default_values = None

    @classmethod
    def init(cls, d):
        obj = cls()
        if not d:
            return None
        for k, v in d.iteritems():
            if not k.startswith("_") and hasattr(obj, k):
                setattr(obj, k, v)
        obj.id = d["_id"].binary
        obj._id = d["_id"]
        if cls.default_values:
            for k,v in cls.default_values.iteritems():
                if k not in d:
                    setattr(obj, k, v)
        return obj

    @classmethod
    def get_by_id(cls, obj_id):
        u = cls.collection.find_one({"_id": ObjectId(obj_id)})
        return cls.init(u)

    @classmethod
    def get(cls, **kwargs):
        u = cls.collection.find_one(kwargs)
        return cls.init(u)

    @classmethod
    def remove(cls, **filter):
        """
        Removes object from the collection
        :param dict filter: dictionary with filters
        :return: number of removed records
        """
        u = cls.collection.remove(filter)
        return u["n"]

    @classmethod
    def update(cls, new_values = None, **filter):
        """
        Updates object.

        :param dict new_values: set of new key/values for object
        :param dict filter: dictionary with filters
        :return: number of changed records
        """
        d = {"$set": new_values}
        u = cls.collection.update(filter, d)
        return u['n']

    @classmethod
    def get_to_return_dict(cls, **filter):
        if "id" in filter:
            filter["_id"] = ObjectId(filter["id"])
            del filter["id"]
        u = cls.collection.find_one(filter)
        if u is None:
            return None
        return cls.to_return_dict(u)

    @classmethod
    def ensure_indexes(cls):
        for columns, param in cls.indexes or []:
            if conf.test:
                param["cache_for"] = 0
            cls.collection.ensure_index(columns, **param)

    @classmethod
    def find_query_re(cls, keys):
        res = {}
        for k, v in keys.iteritems():
            if v:
                res[k] = {"$regex": v}
        return res

    @classmethod
    def to_return_dict(cls, d):
        res = {}
        for k, v in d.iteritems():
            if not k.startswith("_") and hasattr(cls, k):
                res[k] = v
        return res

    @classmethod
    def insert_by_dict(cls, d):
        if cls.default_values:
            for k,v in cls.default_values.iteritems():
                if k not in d:
                    d[k] = v
        cls.collection.insert(d)
