from init import init, BaseAPITestCase
init()

import errors
import unittest

class TestAPI(BaseAPITestCase):

    def __init__(self, *args, **kwargs):
        super(TestAPI, self).__init__(*args, **kwargs)


    def test_user_methods(self):
        password = "testpassword"
        self.post('/0/user/', {"password": password, "display_name": self.display_name, "email": self.email}, auth_required=False)
        self.post('/0/user/', {"password": password, "display_name": self.display_name, "email": self.email}, auth_required=False, expect_errors=errors.UserAlreadyExists)

        self.auth()

        self.get('/0/auth/', {"password": password[:-1], "email": self.email, "deviceid": "id_dev"}, auth_required=False, expect_errors=errors.UserUnauthorized)

        info = self.get('/0/user/', {}).json["user_info"]
        self.assertEqual(info["email"], self.email)
        self.assertEqual(info["display_name"], self.display_name)

        self.post('/0/user/update/', {"display_name": "xxx"})
        info = self.get('/0/user/', {}).json["user_info"]
        self.assertEqual(info["display_name"], "xxx")

        self.post('/0/user/update/', {"password": "xxxyyy"})
        self.get('/0/auth/', {"password": password, "email": self.email, "deviceid": "id_dev"}, expect_errors=errors.UserUnauthorized)
        self.get('/0/auth/', {"password": "xxxyyy", "email": self.email, "deviceid": "id_dev"})

    def test_version(self):
        self.get('/version/', {}, auth_required=False)


if __name__ == '__main__':
    unittest.main()
