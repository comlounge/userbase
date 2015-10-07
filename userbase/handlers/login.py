from starflyer import Handler, redirect
from userbase import db
from userbase.exceptions import *
from logbook import Logger
log = Logger('userbase')


__all__ = ['LoginHandler']


class LoginHandler(Handler):
    """show the user login form and process it"""

    template = "login.html"

    def get(self):
        """show the login form"""
        cfg = self.module.config
        mod = self.module
        form = cfg.login_form
        obj_class = cfg.user_class

        langs = [getattr(self, 'LANGUAGE', 'en')]
        form = cfg.login_form(self.request.form, handler = self)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                try:
                    remember = self.module.config.use_remember and self.request.form.get("remember")
                    user = mod.login(self, **f)
                    url_for_params = cfg.urls.login_success
                    url = self.url_for(**url_for_params)
                    self.flash(self._("Hello %(fullname)s, you are now logged in.") %user)
                    return redirect(url)
                except PasswordIncorrect, e:
                    log.warn("login failed: incorrect password", username = e.username)
                    self.flash(self._("Invalid credentials. You might have mistyped something, please check your spelling."), category="danger")
                except UserUnknown, e:
                    log.warn("login failed: unknown user", username = e.username)
                    self.flash(self._("Invalid credentials. You might have mistyped something, please check your spelling."), category="danger")
                except UserNotActive, e:
                    if cfg.use_double_opt_in:
                        log.warn("login failed: user account not yet activated")
                        self.flash(self._("""Your user account has not been activated. In order to receive a new activation email <a href="%s">click here</a>""") 
                                %self.url_for(".activation_code"), category="warning")
                    else:
                        log.warn("login failed: unknown error", user = user)
                        self.flash(self._("Login failed, please try again."), category="danger")
                except LoginFailed, e:
                    log.error("login failed: unknown error - uncatched exception", username = e.username)
                    self.flash(self._("Login failed, please try again."), category="danger")
        return self.render(form = form)

    post = get
