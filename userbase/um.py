from starflyer import URL, Module, ConfigurationError
from jinja2 import PackageLoader

import handlers
import forms

class UserModule(Module):
    """a module for implementing the user manager"""

    name = "userbase"

    routes = []

    module_jinja_loader = PackageLoader(__name__, "templates/")
    jinja_loader = PackageLoader(__name__, "templates/")

    default_config = {
        'login_handler' : handlers.LoginWithEMail
    }

    ####

    def finalize(self):
        """finalize the configuration"""
        # register the login handler we want to use
        self.add_url_rule(URL("/login", "login", self.config.login_handler))

        # create the database connection

userbase_module = UserModule(__name__)



