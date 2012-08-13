import wtforms                                                                                                                                              

from wtforms import TextField, PasswordField, validators


__all__ = ['login_forms']

class LoginFormEMail(wtforms.Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email()])
    password    = PasswordField('Password', [validators.Length(min=5, max=35)])

class LoginFormUsername(wtforms.Form):
    username       = TextField('Username')
    password    = PasswordField('Password')

login_forms = {
    'login_form_email': LoginFormEMail,
    'login_form_username': LoginFormUsername,
}
