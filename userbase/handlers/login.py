from starflyer import Handler, redirect
from userbase import db
from userbase.exceptions import *

__all__ = ['LoginHandler']


class LoginHandler(Handler):
    """show the user login form and process it"""

    template = "userbase/login.html"

    def get(self):
        """show the login form"""
        cfg = self.module.config
        mod = self.module
        form = cfg.login_form
        obj_class = cfg.user_class

        form = cfg.login_form(self.request.form)
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
                    self.flash(self._("Incorrect password. You might have mistyped your password, please check your spelling."), category="danger")
                except UserUnknown, e:
                    self.flash("Unknown username. You might have mistyped your name, please check your spelling.", category="danger")
                except UserNotActive, e:
                    if cfg.use_double_opt_in:
                        print self._("""Your user account has not been activated. In order to receive a new activation email <a href="%s">click here</a>""") 
                        self.flash(self._("""Your user account has not been activated. In order to receive a new activation email <a href="%s">click here</a>""") 
                                %self.url_for(".activation_code"), category="warning")
                    else:
                        self.flash(self._("Unknown username. You might have mistyped your name, please check your spelling."), category="danger")
                except LoginFailed, e:
                    self.flash(self._("Login failed, please try again."), category="danger")
        return self.render(form = form)

    post = get
