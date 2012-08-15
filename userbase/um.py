from starflyer import URL, Module, ConfigurationError
from jinja2 import PackageLoader
from mongoengine import Q

import handlers
import forms
import db

class UserModule(Module):
    """a module for implementing the user manager"""

    name = "userbase"

    routes = []

    module_jinja_loader = PackageLoader(__name__, "templates/")
    jinja_loader = PackageLoader(__name__, "templates/")

    default_config = {
        'login_handler' : handlers.EMailLoginHandler,
        'user_obj'      : db.UserEMail,
    }

    ####

    def get_render_context(self, handler):
        """inject something into the render context"""
        p = {}
        if "user" in handler.session:
            p['user'] = self.config.user_obj.objects(Q(_id = handler.session['user']), class_check = False)[0]
            p['logged_in'] = True
        return p

    def finalize(self):
        """finalize the configuration"""
        # register the login handler we want to use
        self.add_url_rule(URL("/login", "login", self.config.login_handler))
        self.add_url_rule(URL("/logout", "logout", self.config.login_handler))


userbase_module = UserModule(__name__)



