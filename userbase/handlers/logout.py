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
        del self.session['userid']
        self.flash(cfg.logout_message)
        url_for_params = self.module.config.logout_success_url_params
        url = self.url_for(**url_for_params)
        domain = self.module.config.cookie_domain
        if domain is None:
            domain = self.app.config.session_cookie_domain
        response = redirect(url)
        response.delete_cookie(self.module.config.cookie_name, domain = domain)
        return response

    post = get
