from mongoengine import *
import hashlib

__all__ = ['UserEMail']

class UserEMail(DynamicDocument):
    """a user identified by email address and password"""
    email = EmailField(max_length=200, required=True)
    pw = StringField(max_length=200, required=True)
    fullname = StringField(max_length=200, required=False)

    def set_password(self, pw):
        self.pw = hashlib.new("md5",pw).hexdigest()
        # TODO: generate code

    def get_password(self):
        return self.pw

    password = property(get_password, set_password)

    def check_password(self, pw):
        """check password"""
        hash = hashlib.new("md5",pw).hexdigest()
        return hash == self.pw


    
