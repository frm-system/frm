import conf
from user import User
from utils.request import get, post, delete, put, check_params, Api, ValidateError
from usertoken import UserToken

def TokenId(tokenid):
    token = UserToken.get(tokenid, True)
    if token is None:
        raise ValidateError("Invalid token")
    return token

class UserApi(Api):
    prefix = "user"


    @post("")
    @check_params(email = unicode, display_name = unicode, password = unicode)
    def new_user(self, email, display_name, password):
        """
        Register new user

        :param str email: User email
        :param str display_name: User name
        :param str password: User password in plain text

        :returns: None

        :raise: UserAlreadyExists
        """
        User.new_user(email, password, display_name)
        return {}

    @get('auth/', no_prefix=True)
    @check_params(email = unicode, password = unicode, deviceid = unicode)
    def login(self, email, password, deviceid):
        """
        Returns auth key which should be used for encrypting account credential

        :param str email: User email

        :param str password: User password in plain text

        :param str deviceid: Unique device id (possible IMEA, MAC or like something)

        :returns str tokenid: TokenId which should be used for all following requests.

        """
        tokenid = User.login(email, password, deviceid)
        return {"tokenid": tokenid}

    @post('update/')
    @check_params(token = TokenId, display_name = unicode, password = unicode)
    def update(self, token, display_name = None, password = None):
        """
        Updates user's profile

        :param token: Token which was returned by login method
        :param display_name: New user display name.
        :param password: new password
        :return: None
        """
        User.update(token.userid, display_name, password)
        return {}

    @get('')
    @check_params(token = TokenId)
    def get_info(self, token):
        """
        Returns user's info

        :param token: Token which was returned by login method
        :return dict user_info: Dictionary with users's info's
        """
        user = User.get_by_id(token.userid)
        return {"user_info": {"email": user.email, "display_name": user.display_name}}

