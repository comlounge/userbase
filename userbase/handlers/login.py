from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from userbase.base import UserbaseHandler
from userbase import db
from mongoengine import Q

__all__ = ['UsernameLoginForm', 'EMailLoginForm', 'LoginHandler']

class EMailLoginForm(Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('Password', [validators.Length(min=5, max=35), validators.Required()])
    remember    = BooleanField('remember me, please')

class UsernameLoginForm(Form):
    username    = TextField('Username', [validators.Length(max=200), validators.Required()])
    password    = PasswordField('Password', [validators.Length(min=1, max=35), validators.Required()])
    remember    = BooleanField('remember me, please')

class LoginHandler(UserbaseHandler):
    """show the user login form and process it"""

    template = "_m/userbase/login.html"

    def get(self):
        """show the login form"""
        cfg = self.module.config
        form = cfg.login_form
        obj_class = cfg.user_class

        form = cfg.login_form(self.request.form)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                userid = f[cfg.user_id_field]
                password = f['password']

                # try ot retrieve the user
                users = cfg.user_class.objects(Q(**{cfg.user_id_field : userid}), class_check = False)
                if len(users)==1:
                    user = users[0]
                    if user.check_password(password):
                        url_for_params = self.module.config.login_success_url_params
                        url = self.url_for(**url_for_params)
                        remember = self.module.config.use_remember and self.request.form.get("remember")
                        self.login(user, remember=remember)
                        self.flash(cfg.login_message %user)
                        return redirect(url)
            self.flash("Login failed", category="danger")
        return self.render(form = form)

    post = get
