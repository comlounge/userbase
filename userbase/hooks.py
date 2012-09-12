
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
        return user_data
            
