import uuid 
import string
import os.path
import types

mapping = {
    196 : 'AE', 198 : 'AE', 214 : 'OE', 220 : 'UE', 223 : 'ss', 224 : 'a',
    228 : 'ae', 230 : 'ae', 246 : 'oe', 252 : 'ue'
}

def string2filename(s, path = None, default=u"anonymous"):
    """convert a string to a valid filename"""
    
    from unicodedata import decomposition, normalize

    # TODO: make it a better conversion?
    if type(s) != types.UnicodeType:
        s = unicode(s)
    
    s = s.strip()
    s = s.lower()


    if s=="":
        s = default

    # remove an eventual path
    s = s.replace("\\","/")
    _, s = os.path.split(s)
    
    res = u''
    mkeys = mapping.keys()
    for c in s:
        o = ord(c)
        if o in mapping.keys():
            res = res+mapping[o]
            continue
        if decomposition(c):
            res = res + normalize('NFKD', c)
        else:
            res = res + c
    
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in res if c in valid_chars)
    filename = filename.replace(" ","_")
    
    # if path is not None we can check if there already is a file with that name
    if path is None:
        return filename
        
    fullpath=os.path.join(path, filename)
    if not os.path.exists(fullpath):
        return filename

    # remove the extension
    root, ext = os.path.splitext(filename)
        
    for idx in range(1,100):
        filename = "%s-%d%s" %(root, idx, ext)
        if not os.path.exists(os.path.join(path,filename)):
            return filename
            
    for idx in range(1,100):
        u = unicode(uuid.uuid4())
        filename = "%s-%s%s" %(root, u, ext)
        if not os.path.exists(os.path.join(path,filename)):
            return filename
        
    return None # we did not get a result, TODO: further checking

class Hooks(object):
    """This is a class for holding all kinds of hooks for the user manager related to login, logout, registration
    and so on. You can subclass from it to implement or overwrite your own hooks.

    In ``self.userbase`` you will always find the userbase module, in ``app`` the app and in ``config`` the module
    configuration.
    """

    def __init__(self, userbase):
        """initialize the hooks class"""
        self.userbase = userbase
        self.app = userbase.app
        self.config = userbase.config

    def process_registration_user_data(self, user_data):
        """process the incoming user data (usually from a form) and e.g. fill in username in case an email based 
        form is used"""

        if "username" not in user_data and self.config.user_id_field == "email":
            username = string2filename(user_data.get('fullname', str(uuid.uuid4())))

            prefix = 1
            base = username
            while self.userbase.get_user_by_username(username):
                username = "%s_%s" %(base, prefix)
                prefix = prefix + 1
            user_data['username'] = username
        if "password2" in user_data:
            del user_data['password2']
        user_data['permissions'] = [] # you can set default permissions in your own hook 
        return user_data
            
    def create_activation_code(self, user):
        """create an activation code. Default is a simple uuid"""
        return unicode(uuid.uuid4())

    def create_pw_code(self, user):
        """create a code for pw reset. Default is a simple uuid"""
        return unicode(uuid.uuid4())

    def get_permissions_for_user(self, user, handler=None):
        """this hook is used to retrieve a list of permissions for a given user. You can extend
        this to whatever you want, e.g. based on roles but need to return a list of strings.

        permissions for modules should be prefixed.

        :param user: the user for which we want to retrieve permissions
        :param handler: optional handler which can be passed to get permissions for e.g. a specific location/handler/url
        :return: list of strings describing permissions
        """
        return user.permissions
