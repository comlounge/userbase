from wtforms import Form, TextField, PasswordField, BooleanField, validators, SelectMultipleField, widgets
from wtforms import ValidationError

# check if we have babel installed and update our Form class eventually
try:
    from sfext.babel import T
    from sfext.babel.wtformsupport import I18nForm as Form
except ImportError:
    T = lambda x: x

__all__ = ['UsernameLoginForm', 'EMailLoginForm', 
    'UsernameRegistrationForm', 'EMailRegistrationForm', 
    'UserAddForm', 'UserEditForm', 'PasswordChangeForm',
    'ActivationEMailForm', 'PWEMailForm']

class BaseForm(Form):
    """custom form class for passing in attributes so you can use them in validators. Here we
    use it for the module and config itself
    """
    
    def __init__(self, formdata=None, obj=None, prefix='', module=None, **kwargs):  
        """extend the form with a more data to be stored"""
        self.module = module
        super(BaseForm, self).__init__(formdata=formdata, obj=obj, prefix=prefix, **kwargs)

###
### username based forms
###

class UsernameRegistrationForm(BaseForm):
    username    = TextField(T('Username'),     [validators.Length(max=200), validators.Required()])
    email       = TextField(T('E-Mail'),       [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField(T('Password'), [validators.Required(), validators.EqualTo('password2', message='Passwords must match')])
    password2   = PasswordField(T('Password confirmation'), [validators.Length(max=135), validators.Required()])
    fullname    = TextField(T('Full name'),    [validators.Length(max=200), validators.Required()])

    def validate_email(form, field):
        if form.module.users.find({'email' : field.data}).count() > 0:
            raise ValidationError(T('this email address is already taken'))

    def validate_username(form, field):
        if form.module.users.find({'username' : field.data}).count() > 0:
            raise ValidationError(T('this username is already taken'))


class UsernameLoginForm(Form):
    username    = TextField(T('Username'), [validators.Length(max=200), validators.Required()])
    password    = PasswordField(T('Password'), [validators.Length(max=135), validators.Required()])
    remember    = BooleanField(T('stay logged in'))


###
### email based forms
###

class EMailRegistrationForm(BaseForm):
    email       = TextField('E-Mail',       [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField('Password', [validators.Required(), validators.EqualTo('password2', message='Passwords must match')])
    password2   = PasswordField('Password confirmation', [validators.Length(max=135), validators.Required()])
    fullname    = TextField('Full name',    [validators.Length(max=200), validators.Required()])

    def validate_email(form, field):
        if form.module.users.find({'email' : field.data}).count() > 0:
            raise ValidationError(T('this email address is already taken'))


class EMailLoginForm(Form):
    email       = TextField(T('E-Mail'), [validators.Length(max=200), validators.Email(), validators.Required()])
    password    = PasswordField(T('Password'), [validators.Length(max=135), validators.Required()])
    remember    = BooleanField(T('stay logged in'))



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
    username    = TextField(T('Username'),     [validators.Length(max=200), validators.Required()])
    email       = TextField(T('E-Mail'),       [validators.Length(max=200), validators.Email(), validators.Required()])
    fullname    = TextField(T('Full name'),    [validators.Length(max=200), validators.Required()])
    permissions = PermissionSelectField('Permissions')

class UserAddForm(UserEditForm):
    """user add form is the same as user edit form for now"""

class PasswordChangeForm(BaseForm):
    password    = PasswordField(T('New Password'), [validators.Required(), validators.EqualTo('password2', message=T('Passwords must match'))])
    password2   = PasswordField(T('Password confirmation'), [validators.Length(max=135), validators.Required()])


### activation email form

class ActivationEMailForm(Form):
    """form for asking for an email address to send the code to"""
    email       = TextField(T('E-Mail'), [validators.Length(max=200), validators.Email(), validators.Required()],
                            description = T("Please enter the email address you registered with to receive a new activation code."))

### password forgotten form

class PWEMailForm(Form):
    """form for asking for an email address to send the code to"""
    email       = TextField(T('E-Mail'), [validators.Length(max=200), validators.Email(), validators.Required()],
        description = T("Please enter the email address you registered with to receive a link to reset your password.")
    )

