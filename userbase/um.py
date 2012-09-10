from starflyer import URL, Module, ConfigurationError
from jinja2 import PackageLoader
#from mongoengine import Q
import mongokit
import datetime
import copy

import handlers
from .exceptions import *
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

    name = "userbase"

    routes = []

    module_jinja_loader = PackageLoader(__name__, "templates/")
    jinja_loader = PackageLoader(__name__, "templates/")

    defaults = {
        'login_view'            : 'users.login',
        'logout_view'           : 'users.logout',
        'verification_view'     : 'users.verification',
        'pw_forgotten_view'     : 'users.pw_forgotten',
        'pw_forgotten_code_view' : 'users.pw_forgotten_code',
        'login_message'         : u"You are now logged in, %(fullname)s",
        'logout_message'        : u"You are now logged out",
        'use_remember'          : True, # whether the remember function/cookie is used
        'cookie_secret'         : None,
        'cookie_name'           : "r", # this cookie name is used as the remember cookie
        'cookie_domain'         : None, # means to use the domain from the app
        'cookie_lifetime'       : datetime.timedelta(days=365),
        'master_template'       : "master.html",

        # database related
        'mongodb_host'          : "localhost",
        'mongodb_port'          : 27017,
        'mongodb_name'          : None,
        'mongodb_collection'    : "users",
        'mongodb_kwargs'        : {},

        # endpoint to use after successful login
        'login_success_url_params'  : {'endpoint' : 'root'},
        # endpoint to use after successful logout
        'logout_success_url_params' : {'endpoint' : 'userbase.login'},

        'user_class'            : db.UserEMail,                 # the db class we use for the user
        'user_id_field'         : 'email',                      # the field in the class and form with the id (email or username)
        'login_form'            : handlers.EMailLoginForm,      # the login form to use
        'handler.login'         : handlers.LoginHandler,        # the login handler to use (the generic one)
        'handler.logout'        : handlers.LogoutHandler,
    }


    ####
    #### hooks
    ####

    # module hook
    def finalize(self):
        """finalize the configuration"""
        # open database
        conn = self.connection = mongokit.Connection(
            self.config.mongodb_host,
            self.config.mongodb_port)
        self.collection = conn[self.config.mongodb_name][self.config.mongodb_collection]
        conn.register(self.config.user_class)
        self.users = getattr(self.collection, self.config.user_class.name)

        self.add_url_rule(URL("/login", "login", self.config['handler.login']))
        self.add_url_rule(URL("/logout", "logout", self.config['handler.logout']))

    # handler hooks
    def get_render_context(self, handler):
        """inject something into the render context"""
        p = {}
        user = self.get_user(handler)
        if user is not None and user.is_active:
            p['user'] = user
            p['logged_in'] = True
        return p

    def before_handler(self, handler):
        if self.config.cookie_name in handler.request.cookies and "userid" not in handler.session:
            cookie = self.app.load_cookie(handler.request, self.config.cookie_name)
        else:
            return
        if "userid" not in cookie and "hash" not in cookie:
            return

        # now try to set the token again
        user = self.get_user_by_id(cookie['userid'])
        if user is None:
            return
        if not user.is_active:
            return
        if cookie['hash'] != user.get_token():
            return
        handler.session['userid'] = user.get_id()
        handler.user = user

        # TODO: now reset the remember cookie
        # this means to move save_session from handler to module, better anyway
            
    def after_handler(self, handler, response):
        """check if we need to do a logout"""
        if handler.session.has_key("remember"):
            expires = datetime.datetime.utcnow() + self.config.cookie_lifetime
            self.app.set_cookie(response, self.config.cookie_name, handler.session['remember'], expires = expires)
            del handler.session['remember']
        if handler.session.has_key("remember_forget"):
            self.app.delete_cookie(response, self.config.cookie_name)
            del handler.session['remember_forget']

    ### user related

    def get_user(self, handler):
        """retrieve the user from the handler session or None"""
        return self.get_user_by_id(handler.session.get("userid", None))

    def get_user_by_id(self, userid):
        """returns the user or None if no user was found"""
        return self.users.find_one({self.config.user_id_field : userid})

    def login(self, handler, remember = False, **user_credentials):
        """login a user. What user credentials contains depends on the used data model. In case of very different
        use cases you might also want to override this method. Usually it will be used by the generic login handler.

        :param user_credentials: keyword params containing the credentials for the user
        :return: Returns the user object or an exception in case the login failed
        """
        cfg = self.config
        userid = user_credentials[cfg.user_id_field]
        password = user_credentials['password']
        user = self.get_user_by_id(userid)
        if user is None:
            raise UnknownUser(u"User not found", user_credentials)
        if not user.check_password(password):
            raise IncorrectPassword(u"User not found", user_credentials)

        handler.session['userid'] = user.get_id()

        if remember:
            handler.session['remember'] = {
                'userid' : user.get_id(),
                'hash'   : user.get_token(),
            }
        return user

    def logout(self, handler):
        """log the user out and remove any remaining cookies"""
        del handler.session['userid']
        handler.session['remember_forget'] = True

class EMailUserModule(BaseUserModule):

    defaults = copy.copy(BaseUserModule.defaults)
    defaults.update({
        'user_id_field'         : 'email',
        'login_form'            : handlers.EMailLoginForm,
        'handler.login'         : handlers.LoginHandler,
        'handler.logout'        : handlers.LogoutHandler,
    })


email_userbase = EMailUserModule(__name__)

class UsernameUserModule(BaseUserModule):

    defaults = copy.copy(BaseUserModule.defaults)
    defaults.update({
        'user_class'            : db.UserUsername,                 # the db class we use for the user
        'user_id_field'         : 'username',
        'login_form'            : handlers.UsernameLoginForm,
        'handler.login'         : handlers.LoginHandler,
        'handler.logout'        : handlers.LogoutHandler,
    })

username_userbase = UsernameUserModule(__name__)
