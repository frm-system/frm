import errors
import glob
import json
import os
import unittest
from webtest import TestApp

def init():
    import conf
    conf.test = True

class BaseTestCaseWithoutDB(unittest.TestCase):
    def setUp(self):
        pass

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        from utils.dbconnection import clear_mongo, mongo_ensure_indexes
        clear_mongo()
        from user import User
        mongo_ensure_indexes(User)
        BaseTestCase.load_fixtures()


    @staticmethod
    def load_fixtures():
        from utils.dbconnection import mongo_collection
        current_dir = os.path.dirname(os.path.abspath(__file__))
        pattern = os.path.join(current_dir, "fixtures", "*.json")
        for filename in glob.glob(pattern):
            f = open(filename)
            str_fixture = ''.join(f.readlines())
            if str_fixture:
                name = os.path.basename(filename)
                db = mongo_collection(name[:-5])
                db.insert(json.loads(str_fixture))


class BaseAPITestCase(BaseTestCase):

    def __init__(self, *args, **kwargs):
        import view
        self._app = TestApp(view.application)
        super(BaseAPITestCase, self).__init__(*args, **kwargs)
        self.tokenid = None

        self.email = "email@test.ru"
        self.password = "testpassword"
        self.display_name = "test_display_name"



    def create_user(self):
        # TODO using fixtures instead of creating user and logging
        res = self.post('/0/user/', {"password": self.password, "display_name": "test", "email": self.email}, auth_required=False, expect_errors=True)
        self.assertIn(res.status_code, [200, errors.UserAlreadyExists.default_status])

    def auth(self):
        self.assertIsNotNone(self.email)
        self.assertIsNotNone(self.password)
        self.create_user()
        response = self.get('/0/auth/', {"password": self.password, "email": self.email, "deviceid": "id_dev"}, auth_required=False)
        self.tokenid = response.json["tokenid"]

    def _send(self, method, url, params=None, headers=None, expect_errors=None, auth_required = True):
        params = params or {}
        if auth_required:
            if self.tokenid is None:
                self.auth()
            if "token" not in params:
                params["token"] = self.tokenid
        expect = expect_errors
        expect_errors = expect_errors is not None

        if method == self._app.delete and params is not None:
            import urllib
            url += "?" + urllib.urlencode(params)
            params = ""

        res = method(url = url, params = params, headers = headers,
                     expect_errors = expect_errors)
        if expect is None or expect is True:
            return res
        if isinstance(expect, errors.BadRequest):
            self.assertEqual(res.status_code, expect.default_status)

    def get(self, url, params=None, headers=None, expect_errors=None, auth_required = True):
        return self._send(self._app.get, url, params, headers, expect_errors, auth_required)

    def post(self, url, params=None, headers=None, expect_errors=None, auth_required = True):
        return self._send(self._app.post, url, params, headers, expect_errors, auth_required)

    def delete(self, url, params=None, headers=None, expect_errors=None, auth_required = True):
        return self._send(self._app.delete, url, params, headers, expect_errors, auth_required)

    def put(self, url, params=None, headers=None, expect_errors=None, auth_required = True):
        return self._send(self._app.put, url, params, headers, expect_errors, auth_required)

def dict_diff(first, second, KEYNOTFOUND = '<KEYNOTFOUND>'):
    """ Return a dict of keys that differ with another config object.  If a value is
        not found in one of the configs, it will be represented by KEYNOTFOUND.
        @param first:   Fist dictionary to diff.
        @param second:  Second dictionary to diff.
        @return diff:   Dict of Key => (first.val, second.val)
    """
    diff = {}
    # Check all keys in first dict
    for key in first.keys():
        if not second.has_key(key):
            diff[key] = (first[key], KEYNOTFOUND)
        elif first[key] != second[key]:
            diff[key] = (first[key], second[key])
            # Check all keys in second dict to find missing
    for key in second.keys():
        if not first.has_key(key):
            diff[key] = (KEYNOTFOUND, second[key])
    return diff
