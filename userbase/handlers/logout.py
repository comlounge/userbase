from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, validators
from userbase.base import UserbaseHandler
from userbase import db
from mongoengine import Q

__all__ = ['LogoutHandler']

class LogoutHandler(UserbaseHandler):
    """show the user login form and process it"""

    def get(self):
        """show the login form"""
        cfg = self.module.config
        self.logout()
        self.flash(cfg.logout_message)
        url_for_params = self.module.config.logout_success_url_params
        url = self.url_for(**url_for_params)
        return redirect(url)

    post = get
