from starflyer import URL, Module, ConfigurationError, AttributeMapper
from jinja2 import PackageLoader
import mongokit
import datetime
import copy
import bson

import handlers
from .exceptions import *
import forms
import db
import hooks

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
        'user_class'            : db.User,                      # the db class we use for the user
        'user_id_field'         : 'email',                      # the field in the class and form with the id (email or username)

        # endpoints for redirects
        'urls'                  : AttributeMapper({
            'login_success'         : {'endpoint' : 'root'},
            'registration_success'  : {'endpoint' : 'root'},
            'logout_success'        : {'endpoint' : 'userbase.login'},
        }),

        # in case you want your own handlers
        'handler.login'         : handlers.LoginHandler,        # the login handler to use (the generic one)
        'handler.logout'        : handlers.LogoutHandler,
        'handler.register'      : handlers.RegistrationHandler,        # the login handler to use (the generic one)

        # form related
        'login_form'            : handlers.EMailLoginForm,          # the login form to use
        'registration_form'     : handlers.EMailRegistrationForm,   # the registration form to use
        
        # further settings
        'use_double_opt_in'     : True,                             # use double opt-in?
        'login_after_registration'     : False,                     # directly log in (even without activation)?
        'email_sender_name'     : "Your System",                    # which is the user who sends out codes etc.?
        'email_sender_address'  : "noreply@example.org",            # which is the user who sends out codes etc.?

        # hooks
        'hooks'                 : hooks.Hooks,

        'messages'              : AttributeMapper({
            'user_unknown'              : 'User unknown',
            'password_incorrect'        : 'Your password is not correct',
            'user_not_active'           : 'Your user has not yet been activated.', # maybe provide link here? Needs to be constructed in handler
            'login_failed'              : 'Login failed',
            'login_success'             : 'Welcome, %(fullname)s',
            'logout_success'            : 'Your are now logged out',
            'registration_success'      : 'Your user registration has been successful',
        })
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
        self.add_url_rule(URL("/register", "register", self.config['handler.register']))

        # attach the global hooks
        self.hooks = self.config.hooks(self)

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
        """check if we have a logged in user in the session. If not, check the remember cookie
        and maybe re-login the user
        """
        user = self.get_user_by_id(handler.session.get("userid", None))
        if user is not None:
            handler.user = user
            return
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

    def get_user_by_credential(self, cred):
        """try to retrieve the user by the configured credential field"""
        return self.users.find_one({self.config.user_id_field : cred})

    def get_user_by_id(self, userid):
        """returns the user or None if no user was found"""
        if not isinstance(userid, bson.ObjectId):
            userid = bson.ObjectId(userid)
        return self.users.get_from_id(userid)

    def login(self, handler, remember = False, force = False, **user_credentials):
        """login a user. What user credentials contains depends on the used data model. In case of very different
        use cases you might also want to override this method. Usually it will be used by the generic login handler.

        :param user_credentials: keyword params containing the credentials for the user
        :param remember: If ``True`` the remember cookie will be set, defaults to ``False``
        :param force: If ``True`` the active check for a user will be skipper, defaults to ``False``
        :return: Returns the user object or an exception in case the login failed
        """
        cfg = self.config
        cred = user_credentials[cfg.user_id_field]
        password = user_credentials['password']
        user = self.get_user_by_credential(cred)
        if user is None:
            raise UserUnknown(u"User not found", user_credentials)
        if not user.check_password(password):
            raise PasswordIncorrect(u"Password is wrong", user_credentials)
        if not user.is_active and not force:
            raise UserNotActive(u"the user has not been activated yet", user = user)

        handler.session['userid'] = str(user.get_id())
        handler.user = user
        user.last_login = datetime.datetime.utcnow()
        user.save()

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

    def register(self, user_data):
        """register a new user. ``data`` needs to include all necessary elements for a new user object.
        Depending on the configuration, an activation code will be sent and the user will eventually be logged
        in

        :param user_data: dictionary containing the data for the new user. All required fields need to be present, otherwise a RegistrationFailed exception will be raised. 
        :return: Returns the user object or an exception in case the registration failed
        """
        user_data = self.hooks.process_registration_user_data(user_data)
        user = self.users()
        user.update(user_data)
        user.save()

        
        return user


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
        'user_id_field'         : 'username',
        'login_form'            : handlers.UsernameLoginForm,
        'handler.login'         : handlers.LoginHandler,
        'handler.logout'        : handlers.LogoutHandler,
    })

username_userbase = UsernameUserModule(__name__)
