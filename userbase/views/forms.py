import wtforms

from wtforms import TextField, PasswordField, validators

__all__ = ['LoginFormEMail']

class LoginFormEMail(wtforms.Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email()])
    password    = PasswordField('Password', [validators.Length(min=5, max=35)])
