from utils.request import Api, post, get, check_params
from userapi import TokenId
from contact import Contact
from user import User
import errors

class ContactApi(Api):
    prefix = "contact"

    @post("")
    @check_params(token=TokenId, name=unicode, surname=unicode)
    def new_contact(self, token, name, surname):
        """
        Create new contact
        :param token: which returned by user login
        :param name: Name of the new contact
        :param surname: Surname of the new Contact
        :return:
        """
        user = User.get_by_id(token.userid)
        if not user:
            return errors.UserDoesNotFound()
        Contact.new_contact(user._id, name, surname)
        return {}

