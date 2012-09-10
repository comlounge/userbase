from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from userbase import db
from userbase.exceptions import LoginFailed
from mongoengine import Q

__all__ = ['UsernameLoginForm', 'EMailLoginForm', 'LoginHandler']

class EMailLoginForm(Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('Password', [validators.Length(min=3, max=35), validators.Required()])
    remember    = BooleanField('remember me, please')

class UsernameLoginForm(Form):
    username    = TextField('Username', [validators.Length(max=200), validators.Required()])
    password    = PasswordField('Password', [validators.Length(min=1, max=35), validators.Required()])
    remember    = BooleanField('remember me, please')

class LoginHandler(Handler):
    """show the user login form and process it"""

    template = "_m/userbase/login.html"

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
                    url_for_params = self.module.config.login_success_url_params
                    url = self.url_for(**url_for_params)
                    #self.login(user, remember=remember)
                    self.flash(cfg.login_message %user)
                    return redirect(url)
                except LoginFailed:
                    self.flash("Login failed", category="danger")
        return self.render(form = form)

    post = get
