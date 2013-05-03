from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, validators
from userbase import db

__all__ = ['LogoutHandler']

class LogoutHandler(Handler):
    """show the user login form and process it"""

    def get(self):
        """show the login form"""
        cfg = self.module.config
        self.module.logout(self)
        self.flash(self._(u"You are now logged out."))
        url_for_params = cfg.urls.logout_success
        url = self.url_for(**url_for_params)
        return redirect(url)

    post = get
