from mongoengine import *
import hashlib
import uuid
import datetime

__all__ = ['UserEMail', 'UserUsername']

class UserBase(object):
    """Base class for all users"""


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

    def create_pw(self):
        """create a password"""
        pw = unicode(uuid.uuid4())[:8]
        self.password = pw
        return pw

    def get_id(self):
        """return the userid we want to use in sessions etc."""
        return self._id

    @property
    def is_active(self):
        """overwrite this if you want a different use case"""
        return True

    def create_validation_code(self):
        """create a new validation code"""
        code = self.validationcode = unicode(uuid.uuid4())
        self.validationcode_sent = datetime.datetime.now()
        return code

    def get_token(self):
        """return a token to be used for remembering the user. Per default it's the hashed
        userid:password tuple. So if the password changes this token is not valid anymore
        and the user needs to login again
        """
        return hashlib.new("md5","%s:%s" %(self.get_id(), self.password)).hexdigest()

    

class UserEMail(UserBase, DynamicDocument):
    """a user identified by email address and password"""
    email = EmailField(max_length=200, required=True, primary_key=True)
    pw = StringField(max_length=200, required=True)
    fullname = StringField(max_length=200, required=False)
    meta = {'collection': 'users', 'allow_inheritance': True}

    def get_id(self):
        """return the userid we want to use in sessions etc."""
        return self.email
    
    
class UserUsername(UserBase, DynamicDocument):
    """a user identified by a username and password"""
    email = EmailField(max_length=200, required=True)
    username = StringField(max_length=200, required=True)
    pw = StringField(max_length=200, required=True)
    fullname = StringField(max_length=200, required=False)
    meta = {'collection': 'users', 'allow_inheritance': True}

    def get_id(self):
        """return the userid we want to use in sessions etc."""
        return self.username

