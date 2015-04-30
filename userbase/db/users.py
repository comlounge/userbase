from mongokit import Document, Connection, CustomType
import hashlib
import uuid
import re
import datetime

def email_validator(value):
   email = re.compile(r'(?:^|\s)[-a-z0-9_.]+@(?:[-a-z0-9]+\.)+[a-z]{2,6}(?:\s|$)',re.IGNORECASE)
   return bool(email.match(value))

class Password(CustomType):
    mongo_type = basestring
    python_type = basestring # optional, just for more validation
    init_type = None # optional, fill the first empty value

    def to_bson(self, value):
        """convert type to a mongodb type"""
        # for some reason this is called twice and thus the password is encoded twice. 
        # so this is a workaround
        if value is None:
            return None
        if value.startswith("HASH:"):
            return value
        return "HASH:"+hashlib.new("md5",value.encode("utf-8")).hexdigest()

    def to_python(self, value):
        """convert type to a python object"""
        return value

__all__ = ['UserBase', 'User']

class UserBase(object):
    """Base class for all users"""

    

class User(Document):
    """a user identified by email address and password"""

    name = "User" # should be the same name as the class
    use_dot_notation = True

    def check_password(self, pw):
        """check password"""
        hash = hashlib.new("md5",pw.encode("utf-8")).hexdigest()
        return "HASH:"+hash == self.password

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

    structure = {
        'username'                      : basestring,
        'email'                         : basestring,
        'fullname'                      : basestring,
        'password'                      : Password(),
        'date_creation'                 : datetime.datetime,
        'active'                        : bool,
        'activation_time'               : datetime.datetime,
        'last_login'                    : datetime.datetime,
        'last_ip'                       : basestring,
        'activation_code'               : basestring,
        'activation_code_sent'          : datetime.datetime,
        'activation_code_expires'       : datetime.datetime,
        'pw_code'                       : basestring,
        'pw_code_sent'                  : datetime.datetime,
        'pw_code_expires'               : datetime.datetime,
        'permissions'                   : [basestring],
    }
    
    validators = {
        'email': email_validator,
    }

    required_fields = ['email', 'password', 'date_creation']
    
    default_values = {
        'date_creation'                 : datetime.datetime.utcnow,
        "last_ip"                       : "",
        "last_login"                    : None,
        "activation_time"               : None,
        "activation_code_expires"       : None,
        "activation_code"               : None,
        "pw_code"                       : None,
        "pw_code_expires"               : None,
        "active"                        : False,
        "permissions"                   : [],
    }
    
    def get_id(self):
        """return the userid we want to use in sessions etc."""
        return self._id

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
    
