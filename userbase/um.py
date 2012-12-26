from starflyer import URL, Module, ConfigurationError, AttributeMapper
from jinja2 import PackageLoader
import mongokit
import datetime
import copy
import bson
import pymongo

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

    module_jinja_loader = PackageLoader(__name__, "module_templates/")
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
            'activation'            : {'endpoint' : 'userbase.activate'},
            'activation_success'    : {'endpoint' : 'root'},
            'activation_code_sent'  : {'endpoint' : 'root'},
            'login_success'         : {'endpoint' : 'root'},
            'registration_success'  : {'endpoint' : 'root'},
            'logout_success'        : {'endpoint' : 'userbase.login'},
            'double_opt_in_pending' : {'endpoint' : 'root'},
        }),

        # in case you want your own handlers define them here. They will be set on finalize
        'handler:login'         : handlers.LoginHandler,
        'handler:logout'        : handlers.LogoutHandler,
        'handler:register'      : handlers.RegistrationHandler,     
        'handler:activate'      : handlers.ActivationHandler,      
        'handler:activation_code': handlers.ActivationCodeHandler,

        # form related
        'login_form'            : handlers.EMailLoginForm,          # the login form to use
        'registration_form'     : handlers.EMailRegistrationForm,   # the registration form to use
        'edit_form'             : handlers.UserEditForm,            # the registration form to use
        'add_form'              : handlers.UserAddForm,             # the registration form to use
        
        # further settings
        'enable_registration'   : False,                            # global switch for allowing new users or not
        'enable_usereditor'     : True,                             # global switch for registering the handlers for the user management
        'use_double_opt_in'     : True,                             # use double opt-in?
        'use_html_mail'         : True,                             # use HTML mail? If False, only text mail will be used
        'login_after_registration'     : False,                     # directly log in (even without activation)?
        'email_sender_name'     : "Your System",                    # which is the user who sends out codes etc.?
        'email_sender_address'  : "noreply@example.org",            # which is the user who sends out codes etc.?
        'subjects'              : AttributeMapper({
            'registration'      : 'Your registration is nearly finished',
            'welcome'           : 'Welcome to our system',
            'password'          : 'Password reminder',
        }),
        'emails'                : AttributeMapper({
            'activation_code'   : '_m/userbase/emails/activation_code',
            'welcome'           : '_m/userbase/emails/welcome',
        }),
            
        # hooks
        'hooks'                 : hooks.Hooks,

        'messages'              : AttributeMapper({
            'user_unknown'              : 'User unknown',
            'email_unknown'             : 'This email address cannot not be found in our user database',
            'password_incorrect'        : 'Your password is not correct',
            'user_not_active'           : 'Your user has not yet been activated.', # maybe provide link here? Needs to be constructed in handler
            'login_failed'              : 'Login failed',
            'login_success'             : 'Welcome, %(fullname)s',
            'logout_success'            : 'Your are now logged out',
            'double_opt_in_pending'     : 'To finish the registration process please check your email with instructions on how to activate your account.',
            'registration_success'      : 'Your user registration has been successful',
            'activation_success'        : 'Your account has been activated',
            'activation_failed'         : 'The activation code is not valid. Please try again or click <a href="%(url)s">here</a> to get a new one.',
            'activation_code_sent'      : 'A new activation code has been sent out, please check your email',
            'already_active'            : 'The user is already active. Please log in.',
            
            # for user manager
            'user_edited'               : 'The user has been updated.',
            'user_added'                : 'The user has been added.',
            'user_deleted'              : 'The user has been deleted.',
            'user_activated'            : 'The user has been activated.',
            'user_deactivated'          : 'The user has been deactivated.',
        }),

        'permissions'           : AttributeMapper({
            'userbase:admin'    : "manage users",
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

        self.add_url_rule(URL("/login", "login", self.config['handler:login']))
        self.add_url_rule(URL("/logout", "logout", self.config['handler:logout']))
        if self.config.enable_registration:
            self.add_url_rule(URL("/register", "register", self.config['handler:register']))
            self.add_url_rule(URL("/activate", "activate", self.config['handler:activate']))
            self.add_url_rule(URL("/activation_code", "activation_code", self.config['handler:activation_code']))
        if self.config.enable_usereditor:
            self.add_url_rule(URL("/admin/", "userlist", handlers.UserList))
            self.add_url_rule(URL("/admin/new", "useradd", handlers.UserAdd))
            self.add_url_rule(URL("/admin/<uid>", "useredit", handlers.UserEdit))
            self.add_url_rule(URL("/admin/<uid>/activate", "useractivate", handlers.UserActivate))

        # attach the global hooks
        self.hooks = self.config.hooks(self)

    # handler hooks
    def get_render_context(self, handler):
        """inject something into the render context"""
        p = {}
        user = self.get_user(handler)
        if user is not None and user.active:
            p['user'] = user
            p['logged_in'] = True
        return p

    def before_handler(self, handler):
        """check if we have a logged in user in the session. If not, check the remember cookie
        and maybe re-login the user
        """
        handler.user = None
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
        if not user.active:
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

    def get_user_by_activation_code(self, code):
        """try to retrieve the user by the configured credential field"""
        if code is None:
            return None
        return self.users.find_one({'activation_code': code})

    def get_user_by_email(self, email):
        """try to retrieve the user by the email address"""
        return self.users.find_one({'email': email})

    def get_user_by_username(self, username):
        """try to retrieve the user by the username"""
        return self.users.find_one({'username': username})

    def get_users_by(self, key, value):
        """return a list of users which field ``key`` matches ``value``"""
        return self.users.find({key: value})

    def get_user_by_id(self, userid):
        """returns the user or None if no user was found"""
        if not isinstance(userid, bson.ObjectId):
            try:
                userid = bson.ObjectId(userid)
            except pymongo.errors.InvalidId:
                return None
        return self.users.get_from_id(userid)

    def login(self, handler, remember = False, force = False, user = None, save = True, **user_credentials):
        """login a user. What user credentials contains depends on the used data model. In case of very different
        use cases you might also want to override this method. Usually it will be used by the generic login handler.

        :param user: in case you already have the user object you can use this to login. credentials are ignored in this case. Usually used on registration etc.
        :param save: if ``True`` the user object will be saved (after setting last login date). ``False`` means that you will do it anyway (e.g. on registration). Defaults to ``True``
        :param user_credentials: keyword params containing the credentials for the user
        :param remember: If ``True`` the remember cookie will be set, defaults to ``False``
        :param force: If ``True`` the active check for a user will be skipper, defaults to ``False``
        :return: Returns the user object or an exception in case the login failed
        """
        cfg = self.config
        if user is None:
            cred = user_credentials[cfg.user_id_field]
            password = user_credentials['password']
            user = self.get_user_by_credential(cred)
            if user is None:
                raise UserUnknown(u"User not found", user_credentials)
            if not user.check_password(password):
                raise PasswordIncorrect(u"Password is wrong", user_credentials)
        if not user.active and not force:
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

    def register(self, user_data, force = False, create_pw = True):
        """register a new user. ``data`` needs to include all necessary elements for a new user object.
        Depending on the configuration, an activation code will be sent and the user will eventually be logged
        in

        :param user_data: dictionary containing the data for the new user. All required fields need to be present, otherwise a RegistrationFailed exception will be raised. 
        :param force: If ``True`` it does not send any opt in and the user is active directly. Defaults to ``False``. 
        :param create_pw: If ``True`` a password for the user is created by calling the user object's ``create_pw()``. Defaults to ``False``
        :return: Returns the user object or an exception in case the registration failed
        """
        user_data = self.hooks.process_registration_user_data(user_data)
        user = self.users()
        user.update(user_data)
        if self.config.double_opt_in and not force:
            user.active = False
            self.send_activation_code(user)
        else:
            user.active = True
        if create_pw:
            user.create_pw()
        user.save()
        return user

    def send_activation_code(self, user):
        cfg = self.config
        code = self.hooks.create_activation_code(user)
        user.set_activation_code(code)
        user.save()
        url = self.app.url_for(_append = True, _full = True, code = code, **self.config.urls.activation)
        self.send_email(cfg.emails.activation_code, cfg.subjects.registration, user.email, user = user, url = url, code = code)

    def send_welcome_mail(self, user):
        url = self.app.url_for(_full = True, **self.config.urls.welcome)
        self.send_email(self.config.emails.welcome, cfg.subjects.welcheom, user.email, user = user, url = url)

    def send_email(self, tmplname, subject, to, **kw):
        """send an email template out. 

        :param subject: The subject to use
        :param template: The name of the template without any extension. This will be added depending on whether we send html emails or not
        :param user: the user for which we want to send the template
        """
        mailer = self.app.module_map['mail']
        if self.config.use_html_mail:
            html = self.app.jinja_env.get_or_select_template(tmplname+".html").render(**kw)
            txt = self.app.jinja_env.get_or_select_template(tmplname+".txt").render(**kw)
            mailer.mail_html(to, subject, txt, html)
        else:
            txt = self.app.jinja_env.get_or_select_template(tmplname+".txt").render(**kw)
            mailer.mail(to, subject, txt)


class EMailUserModule(BaseUserModule):

    defaults = copy.copy(BaseUserModule.defaults)
    defaults.update({
        'user_id_field'         : 'email',
        'login_form'            : handlers.EMailLoginForm,
        'handler:login'         : handlers.LoginHandler,
        'handler:logout'        : handlers.LogoutHandler,
    })


email_userbase = EMailUserModule(__name__)

class UsernameUserModule(BaseUserModule):

    defaults = copy.copy(BaseUserModule.defaults)
    defaults.update({
        'user_id_field'         : 'username',
        'login_form'            : handlers.UsernameLoginForm,
        'handler:login'         : handlers.LoginHandler,
        'handler:logout'        : handlers.LogoutHandler,
        'registration_form'     : handlers.UsernameRegistrationForm,
    })

username_userbase = UsernameUserModule(__name__)
