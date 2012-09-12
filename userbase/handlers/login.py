from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from userbase import db
from userbase.exceptions import LoginFailed

__all__ = ['UsernameLoginForm', 'EMailLoginForm', 'LoginHandler']

class EMailLoginForm(Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('Password', [validators.Length(max=135), validators.Required()])
    remember    = BooleanField('remember me, please')

class UsernameLoginForm(Form):
    username    = TextField('Username', [validators.Length(max=200), validators.Required()])
    password    = PasswordField('Password', [validators.Length(max=135), validators.Required()])
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
                    url_for_params = cfg.urls.login_success
                    url = self.url_for(**url_for_params)
                    self.flash(cfg.messages.login_success %user)
                    return redirect(url)
                except PasswordIncorrect, e:
                    self.flash(cfg.messages['password_incorrect'], category="danger")
                except UserUnknown, e:
                    self.flash(cfg.messages['user_unknown'], category="danger")
                except UserNotActive, e:
                    self.flash(cfg.messages['user_unknown'], category="danger")
                except LoginFailed, e:
                    self.flash(cfg.messages['login_failed'], category="danger")
        return self.render(form = form)

    post = get
