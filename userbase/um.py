from starflyer import URL, Module, ConfigurationError
from jinja2 import PackageLoader
from mongoengine import Q

import handlers
import forms
import db

__all__ = [
    'BaseUserModule', 
    'EMailUserModule',
    'UsernameUserModule',
    'username_userbase',
    'email_userbase',
]

"""

cookie and user handling in userbase

The userid is generally stored in the handler session. By calling ``get_user()`` from
the userbase module this will be retrieved (None if not present). 

To remember a user we store an additional cookie which can be configured by the data above. 
We need to be able to invalidate that information though if the user changes his password or
if it is changed or the user is deactivated. The following cases can happen:

- the user changes his password. In this case the userbase cookie must be updated
- the admin deletes/deactivates the user. Once the user comes back the cookie should not match anymore. 

So we need some token which changes and which can be checked. This is what the ``get_token()`` method
of the user object should implement. Usually it can be just the hashed userid. But it could also be
e.g. hash(userid:password). If the user is inactive then it should return None. 

The cookie itself stores both the userid and the token. This way we can fetch the user and
check the token. We also use a secure cookie for it and you can set the cookie secret seperately 
for the user.

"""


class BaseUserModule(Module):
    """a module for implementing the user manager"""

    name = "users"

    routes = []

    module_jinja_loader = PackageLoader(__name__, "templates/")
    jinja_loader = PackageLoader(__name__, "templates/")

    default_config = {
        'login_view'            : 'users.login',
        'logout_view'           : 'users.logout',
        'verification_view'     : 'users.verification',
        'pw_forgotten_view'     : 'users.pw_forgotten',
        'pw_forgotten_code_view' : 'users.pw_forgotten_code',
        'login_message'         : u"You are now logged in",
        'logout_message'        : u"You are now logged out",
        'cookie_secret'         : None,
        'cookie_name'           : "ru",
        'cookie_domain'         : None, # means to use the domain from the app
        'cookie_lifetime'       : datetime.timedelta(days=365)

        'user_obj'              : db.UserEMail,
        'user_id_field'         : 'email',
        'handler.login'         : handlers.EMailLoginHandler,
        'handler.logout'        : handlers.EMailLoginHandler,
    }

    ####

    def get_render_context(self, handler):
        """inject something into the render context"""
        p = {}
        if "user" in handler.session:
            p['user'] = self.config.user_obj.objects(Q(_id = handler.session['user']), class_check = False)[0]
            p['logged_in'] = True
        return p

    def get_user(self, handler):
        """retrieve the user from the handler session or None"""
        if "user" in handler.session:
            return self.config.user_obj.objects(Q(_id = handler.session['user']), class_check = False)[0]
        return None

    def finalize(self):
        """finalize the configuration"""
        self.add_url_rule(URL("/login", "login", self.config['handler.login']))
        self.add_url_rule(URL("/logout", "logout", self.config['handler.logout']))


#userbase_module = UserModule(__name__)


class EmailUserModule(Module):

    default_config.update({
        'user_id_field'         : 'email',
        'handler.login'         : handlers.LoginHandler,
        'handler.logout'        : handlers.LoginHandler,
    })


email_userbase = EMailUserModule(__name__)

class UsernameBasedUserModule(Module):

    default_config.update({
        'user_id_field'         : 'username',
        'handler.login'         : handlers.LoginHandler,
        'handler.logout'        : handlers.LoginHandler,
    })

username_userbase = UsernameUserModule(__name__)
