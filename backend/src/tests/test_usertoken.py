import unittest

import conf
conf.test = True

from usertoken import UserToken

class UserTokenTest(unittest.TestCase):
    def test_generation(self):
        userid = "xzcsdfjsdlfj"
        token = UserToken.new(userid)
        tokenid = token.tokenid

        token2 = UserToken.get(tokenid)
        self.assertEqual(token.userid, token2.userid)


        token3 = UserToken.get("xxxyyy")
        self.assertIsNone(token3)

if __name__ == '__main__':
    unittest.main()
