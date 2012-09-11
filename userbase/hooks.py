
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

