from wtforms import Form, TextField, PasswordField, BooleanField, validators, SelectMultipleField, widgets
from wtforms import ValidationError

__all__ = ['UsernameLoginForm', 'EMailLoginForm', 
    'UsernameRegistrationForm', 'EMailRegistrationForm', 
    'UserAddForm', 'UserEditForm', 'PasswordChangeForm']

class BaseForm(Form):
    """custom form class for passing in attributes so you can use them in validators. Here we
    use it for the module and config itself
    """
    
    def __init__(self, formdata=None, obj=None, prefix='', module=None, **kwargs):
        super(BaseForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)
        self.module = module                                                                                                                                                         

###
### username based forms
###

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


class UsernameLoginForm(Form):
    username    = TextField('Username', [validators.Length(max=200), validators.Required()])
    password    = PasswordField('Password', [validators.Length(max=135), validators.Required()])
    remember    = BooleanField('remember me, please')


###
### email based forms
###

class EMailRegistrationForm(BaseForm):
    email       = TextField('E-Mail',       [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('New Password', [validators.Required(), validators.EqualTo('password2', message='Passwords must match')])
    password2   = PasswordField('Password confirmation', [validators.Length(max=135), validators.Required()])
    fullname    = TextField('Full name',    [validators.Length(max=200), validators.Required()])

    def validate_email(form, field):
        if form.module.users.find({'email' : field.data}).count() > 0:
            raise ValidationError('this email is already taken')


class EMailLoginForm(Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('Password', [validators.Length(max=135), validators.Required()])
    remember    = BooleanField('remember me, please')



###
### combined form for user manager
###

class PermissionSelectField(SelectMultipleField):
    """extended select field which takes possible permissions and their names from the module"""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

    def __init__(self, label=None, validators=None, _form = None, **kwargs):
        super(SelectMultipleField, self).__init__(label, validators, **kwargs)
        self.form = _form

    def pre_validate(self, form):
        if self.data:                                                                                                      
            values = list(c[0] for c in self.iter_choices())
            for d in self.data:
                if d not in values:
                    raise ValueError(self.gettext(u"'%(value)s' is not a valid choice for this field") % dict(value=d))
        
    
    def iter_choices(self):
        if self.data is None:
            d = []
        else:
            d = self.data
        cfg = self.form.module.config
        choices = cfg.permissions
        for perm, name in choices.items():
            yield (perm, name, self.coerce(perm) in d)

class UserEditForm(BaseForm):
    username    = TextField('Username',     [validators.Length(max=200), validators.Required()])
    email       = TextField('E-Mail',       [validators.Length(max=200), validators.Email(), validators.Required()])
    fullname    = TextField('Full name',    [validators.Length(max=200), validators.Required()])
    permissions = PermissionSelectField('Permissions')

class UserAddForm(UserEditForm):
    """user add form is the same as user edit form for now"""

class PasswordChangeForm(BaseForm):
    password    = PasswordField('New Password', [validators.Required(), validators.EqualTo('password2', message='Passwords must match')])
    password2   = PasswordField('Password confirmation', [validators.Length(max=135), validators.Required()])
