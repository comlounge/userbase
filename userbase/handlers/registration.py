from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from userbase import db

__all__ = ['UsernameRegistrationForm', 'EMailRegistrationForm', 'RegistrationHandler']

class UsernameRegistrationForm(Form):
    email       = TextField('E-Mail',       [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('Password', [validators.Length(max=135), validators.Required()])
    password2   = PasswordField('Password confirmation', [validators.Length(max=135), validators.Required()])
    fullname    = TextField('Full name',    [validators.Length(max=200), validators.Required()])

class EMailRegistrationForm(Form):
    username    = TextField('Username',     [validators.Length(max=200), validators.Required()])
    email       = TextField('E-Mail',       [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('Password', [validators.Length(max=135), validators.Required()])
    password2   = PasswordField('Password confirmation', [validators.Length(max=135), validators.Required()])
    fullname    = TextField('Full name',    [validators.Length(max=200), validators.Required()])

class RegistrationHandler(Handler):
    """show the registration form and process it"""

    template = "_m/userbase/registration.html"

    def get(self):
        """show the registration form"""
        cfg = self.module.config
        mod = self.module
        form = cfg.registration_form
        obj_class = cfg.user_class

        form = form(self.request.form)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user, message = mod.register(self, **f)
                self.flash(message)
                url_for_params = self.module.config.login_success_url_params
                url = self.url_for(**url_for_params)
                return redirect(url)
        return self.render(form = form)

    post = get
