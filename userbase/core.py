from starflyer import AttributeMapper
import colander
import hashlib
import uuid
import datetime
import mongoquery.onrm as onrm
__all__ = ['User', 'UserManager', 'UserSchema']

class Roles(colander.SequenceSchema):
    role = colander.SchemaNode(colander.String())

class UserSchema(colander.MappingSchema):
    """the most basic schema for a user. You can extend it to your liking though.
    Note that we use the email address as main identifier but you can change this
    yourself to any other field. You should make sure it's indexed though if you expect
    a lot of users.
    """
    email = colander.SchemaNode(colander.String(), validator = colander.Email())
    name = colander.SchemaNode(colander.String(), validator = colander.Length(6,200))
    password = colander.SchemaNode(colander.String(), validator = colander.Length(6))
    state = colander.SchemaNode(colander.String(), missing="initialized")
    validation_code = colander.SchemaNode(colander.String(), missing="")
    validation_code_sent = colander.SchemaNode(onrm.DateTime(), missing="")
    pw_code = colander.SchemaNode(colander.String(), missing="")
    pw_code_sent = colander.SchemaNode(onrm.DateTime(), missing="")
    last_logged_in = colander.SchemaNode(onrm.DateTime(), missing="")

class User(onrm.Record):
    """A user record. 

    For validation we use the following workflow:

    initialized
        a new user has been created.
    code_sent
        a verification code has been sent to the user
    active
        a verification code has been validated. The user is full active

   
    Moreover we support a password verification code which is sent in order to set a new password.

    Both codes have a date stored on which they have been sent so we can check for timed validity.
    """
    
    schema = UserSchema()
    create_id = True

    def set_pw(self, pw):
        """store a password"""
        self.d.password = hashlib.new("md5",pw).hexdigest()
        return pw

    def check_pw(self, pw):
        """check if the given password is correct"""
        hash = hashlib.new("md5",pw).hexdigest()
        return hash == self.d.password

    def gen_code(self):
        """generate a new validation code"""
        return unicode(uuid.uuid4())[:12]

    def send_validation_code(self, url_for):
        """generate and send a new validation code"""
        if self.d.state not in ("initialized", "code_sent"):
            # TODO: raise something here?
            return
        self.d.validation_code = self.gen_code()
        self.d.validation_code_sent = datetime.datetime.now()
        # TODO: actually sent the code
        self.d.state = "code_sent"
        valcode_link = url_for("validation", code = self.d.validation_code, force_external=True)
        self.collection.config.mail.mailer.mail("%s <%s>" %(self.d.name, self.d.email), "Registration", "welcome.txt",
            valcode = self.d.validation_code,
            valcode_link = valcode_link)

    def send_pw_forgotten_code(self, url_for):
        """generate and send a new password forgotten code"""
        self.d.pw_code = self.gen_code()
        self.d.pw_code_sent = datetime.datetime.now()
        pw_link = url_for("pw_validation", code = self.d.pw_code, force_external=True)
        self.collection.config.mail.mailer.mail("%s <%s>" %(self.d.name, self.d.email), "Passwort vergessen", "pw_forgotten.txt",
            pw_code = self.d.pw_code,
            pw_link = pw_link)

    def save(self):
        """save the object"""
        self.collection.put(self)

class UserManager(onrm.Collection):
    """the user manager which handles users on the API level"""

    data_class = User
    identifier = "email"
    use_objectids = False # does the mongodb collection use object ids?

    def __init__(self, collection, config={}):
        """initialize the user manager

        :param collection: The MongoDB collection object to be used to store asset data
        :param config: A dictionary containing configuration for the Media Database

        """
        super(UserManager, self).__init__(collection, config)

    def on_put(self, obj, data):
        """check for duplicate emails"""
        if not obj.from_db:
            email = obj.d.email
            if self.find_by_email(email) is not None:
                raise onrm.InvalidData({'email' : 'already exists'})
        return data

    def find_by_email(self, email):
        """return a user by email or None"""
        q = self.query.update(email = email)
        res = q()
        if res.count==0:
            return None
        return res[0]

    def find_by_code(self, code):
        """return a User object by validation code"""
        q = self.query.update(validation_code = code)
        res = q()
        if res.count==0:
            return None
        return res[0]

    def find_by_pwcode(self, code):
        """return a User object by password validation code"""
        q = self.query.update(pw_code = code)
        res = q()
        if res.count==0:
            return None
        return res[0]

    def __getitem__(self, ident):
        """return the user defined by the identifier given"""
        q = self.query
        q.update(**{self.identifier : ident})
        res = q()
        if res.count == 0:
            return None
        return list(res)[0]

