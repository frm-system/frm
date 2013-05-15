from utils.basemodel import Model
from utils.dbconnection import mongo_collection


class Contact(Model):
    id = None
    userid = None
    name = None
    surname = None
    collection = mongo_collection("contact")


    @staticmethod
    def new_contact(userid, name, surname):
        Contact.collection.insert({"userid": userid, "name": name, "surname": surname})