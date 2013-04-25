import bcrypt
import conf
import errors

from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from usertoken import UserToken
from utils.dbconnection import mongo_collection
from utils.basemodel import Model

class User(Model):
    id = None
    email = None
    role = None
    display_name = None
    password = None
    auth_provider = None
    auth_token = None
    ip = None
    geo = None
    collection = mongo_collection("user")
    indexes = [
        ( [("email", 1)], {"unique": True}),
        ]


    ADMIN_USER = 0
    MODERATOR_USER = 1
    configuration = conf.user

    def __init__(self):
        pass

    def generate_token(self):
        token = UserToken.new(self.id)
        return token.tokenid

    @classmethod
    def get_by_email(cls, email):
        return User.get(email = email)

    @staticmethod
    def password_hashing(raw_password):
        hashed = bcrypt.hashpw(raw_password, bcrypt.gensalt(User.configuration.salt_rounds))
        return hashed

    def check_password(self, raw_password):
        return bcrypt.hashpw(raw_password, self.password) == self.password

    @staticmethod
    def new_user(email, password, display_name):
        passwd = User.password_hashing(password)
        try:
            User.collection.insert({"email": email, "password": passwd, "display_name": display_name})
        except DuplicateKeyError:
            raise errors.UserAlreadyExists()

    @staticmethod
    def login(email, password, deviceid):
        user = User.get_by_email(email)
        if user is None:
            DEBUG("User %s is not found" % email)
            raise errors.UserUnauthorized()
        if not user.check_password(password):
            DEBUG("Password mismatch for user %s" % email)
            raise errors.UserUnauthorized()
        return user.generate_token()

    @staticmethod
    def update(userid, display_name = None, password = None):
        updates = {}
        if display_name:
            updates["display_name"] = display_name
        if password:
            updates["password"] = User.password_hashing(password)
        User.collection.update({"_id": ObjectId(userid)}, {"$set": updates})
        return {}
