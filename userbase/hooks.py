import uuid 

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
            user_data['username'] = user_data['email']
        if "password2" in user_data:
            del user_data['password2']
        user_data['permissions'] = [] # you can set default permissions in your own hook 
        return user_data
            
    def create_activation_code(self, user):
        """create an activation code. Default is a simple uuid"""
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
