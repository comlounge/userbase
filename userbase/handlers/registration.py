from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from wtforms import ValidationError
from userbase import db

__all__ = ['UsernameRegistrationForm', 'EMailRegistrationForm', 'RegistrationHandler']

class BaseForm(Form):
    """custom form class for passing in attributes so you can use them in validators. Here we
    use it for the module and config itself
    """
    
    def __init__(self, formdata=None, obj=None, prefix='', module=None, **kwargs):
        super(BaseForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.module = module                                                                                                                                                         

class UsernameRegistrationForm(BaseForm):
    username    = TextField('Username',     [validators.Length(max=200), validators.Required()])
    email       = TextField('E-Mail',       [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('New Password', [validators.Required(), validators.EqualTo('password2', message='Passwords must match')])
    password2   = PasswordField('Password confirmation', [validators.Length(max=135), validators.Required()])
    fullname    = TextField('Full name',    [validators.Length(max=200), validators.Required()])

    def validate_email(form, field):
        if form.module.users.find({'email' : field.data}).count() > 0:
            raise ValidationError('this email is already taken')

    def validate_username(form, field):
        if form.module.users.find({'username' : field.data}).count() > 0:
            raise ValidationError('this username is already taken')


class EMailRegistrationForm(BaseForm):
    email       = TextField('E-Mail',       [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('New Password', [validators.Required(), validators.EqualTo('password2', message='Passwords must match')])
    password2   = PasswordField('Password confirmation', [validators.Length(max=135), validators.Required()])
    fullname    = TextField('Full name',    [validators.Length(max=200), validators.Required()])

    def validate_email(form, field):
        if form.module.users.find({'email' : field.data}).count() > 0:
            raise ValidationError('this email is already taken')


class RegistrationHandler(Handler):
    """show the registration form and process it"""

    template = "_m/userbase/registration.html"

    def get(self):
        """show the registration form"""
        cfg = self.module.config
        mod = self.module
        form = cfg.registration_form
        obj_class = cfg.user_class

        form = form(self.request.form, module = self.module)
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
