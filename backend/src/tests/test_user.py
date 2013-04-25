from init import init, BaseTestCase
init()

import errors
import unittest
from user import User


class TestUser(BaseTestCase):

    def test_password_hashing(self):
        password = "test+password"
        hashed = User.password_hashing(password)
        user = User()
        user.password = hashed

        self.assertTrue(user.check_password(password))
        self.assertFalse(user.check_password(password+"1"))
        self.assertFalse(user.check_password(password[:-1]))

    def test_new_user(self):
        User.new_user("test@test.ru", "password", "Cool name")

        with self.assertRaises(errors.UserAlreadyExists) as r:
            User.new_user("test@test.ru", "password", "Cool name")

if __name__ == '__main__':
    unittest.main()
