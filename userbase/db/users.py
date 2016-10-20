import hashlib
import uuid
import re
import datetime
from mongogogo import *


class UserSchema(Schema):
    """main schema for a barcamp holding all information about core data, events etc."""

    created                     = DateTime()
    updated                     = DateTime()
    username                    = String(required = True)
    email                       = String(required = True)
    fullname                    = String()
    _password                    = String(required = True)
    active                      = Boolean(default = False)
    activation_time             = DateTime()
    last_login                  = DateTime()
    last_ip                     = String()
    activation_code             = String()
    activation_code_sent        = DateTime()
    activation_code_expires     = DateTime()
    pw_code                     = String()
    pw_code_sent                = DateTime()
    pw_code_expires             = DateTime()
    permissions                 = List(String())

    bad_login_attempts          = Integer()
    last_failed_login           = DateTime()

class User(Record):
    """a user identified by email address and password"""

    schema = UserSchema()
    _protected = ['schema', 'collection', '_protected', '_schemaless', 'password', 'default_values']
    default_values = {
        "created"                       : datetime.datetime.utcnow,
        "updated"                       : datetime.datetime.utcnow,
        "last_ip"                       : "",
        "last_login"                    : None,
        "activation_time"               : None,
        "activation_code_expires"       : None,
        "activation_code"               : None,
        "pw_code"                       : None,
        "pw_code_expires"               : None,
        "active"                        : False,
        "permissions"                   : [],
        "bad_login_attempts"            : 0,
        "last_failed_login"             : None,
    }

    def _old_compute_pw(self, pw):
        """old version to store passwords which we want to get rid of"""
        return "HASH:" + hashlib.new("md5",(self.collection.SALT+pw).encode("utf-8")).hexdigest()
        
    def _compute_pw(self, pw):
        """new version on computing password a much more safer way using passlib"""
        ctx = self.collection.md.pw_context
        return ctx.encrypt(pw)

    def __init__(self, doc={}, from_db = None, collection = None, *args, **kwargs):
        """override the constructor to set the password properly if given"""

        # need this for the password context and SALT
        self.collection = collection

        if "password" in doc:
            doc['_password'] = self._compute_pw(doc['password'])

        return super(User, self).__init__(doc = doc, from_db = from_db, collection = collection, *args, **kwargs)

    def update(self, doc = {}):
        """setting the password here, too"""
        if "password" in doc:
            doc['_password'] = self._compute_pw(doc['password'])
        super(User, self).update(doc)
  
    def check_password(self, pw):
        """check password"""
        hashed = self._password
        if hashed.startswith("$pbkdf2"):
            # new password style
            success = self.collection.md.pw_context.verify(pw, hashed)
        else:
            success = self._old_compute_pw(pw) == self._password
            if success:
                # lets update the user
                self._password = self.collection.md.pw_context.encrypt(pw)
                self.collection.save(self)

        if not success:
            self.last_failed_login = datetime.datetime.utcnow()
            if not self.bad_login_attempts:
                self.bad_login_attempts = 1
            else:
                self.bad_login_attempts = self.bad_login_attempts + 1
        else:
            self.last_failed_login = None
            self.bad_login_attempts = 0
        self.collection.save(self)
        return success

    def get_password(self):
        """just return the encrypted password"""
        return self._password

    def set_password(self, pw):
        """encrypt and save the password"""
        self._password = self._compute_pw(pw)
    
    password = property(get_password, set_password)

    def create_pw(self, l=8):
        """create a password for the user and store it in the password field

        :param l: The length of the password to generate. Defaults to 8.
        """
        pw = unicode(uuid.uuid4())[:l]
        self.password = pw
        return pw

    def get_id(self):
        """return the userid we want to use in sessions etc."""
        return self._id

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

    def set_activation_code(self, code, duration = None):
        if duration is None:
            duration = datetime.timedelta(days=1)
        if type(duration) == type(2):
            duration = datetime.timedelta(seconds = duration)
        expires = datetime.datetime.utcnow() + duration
        self.activation_code = code
        self.activation_code_sent = datetime.datetime.utcnow()
        self.activation_code_expires = expires

    def activate(self):
        """activate the user"""
        self.active = True
        self.activation_time = datetime.datetime.utcnow()
        self.activation_code = None
        self.activation_expires = None

    def set_pw_code(self, code, duration = None):
        if duration is None:
            duration = datetime.timedelta(days=1)
        if type(duration) == type(2):
            duration = datetime.timedelta(seconds = duration)
        expires = datetime.datetime.utcnow() + duration
        self.pw_code = code
        self.pw_code_sent = datetime.datetime.utcnow()
        self.pw_code_expires = expires
    
    def has_permission(self, permission):
        """checks if the user has a given permission. Returns ``True`` if so otherwise ``False``
        """
        return permission in self.permissions

    @property
    def fullname(self):
        """return the fullname or the username if no fullname is given"""
        if self['fullname'] != '':
            return self['fullname']
        return self['username']
    

class Users(Collection):
    """the user collection"""

    data_class = User
    SALT = ""


    def before_serialize(self, obj):
        """make sure email and username are lowercase before serializing"""
        if obj.has_key("email"):
            obj['email'] = obj['email'].lower()
        if obj.has_key("username"):
            obj['username'] = obj['username'].lower()
        return obj


