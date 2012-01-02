from framework import Handler
from starflyer import ashtml

from wtforms import Form, TextField, validators, TextAreaField, PasswordField

class LoginForm(Form):
    email       = TextField('Email-Adresse:', [validators.Length(min=6, max=35), validators.Email()])
    password    = PasswordField('Passwort:', [validators.Length(min=6, max=35)])

class IndexView(Handler):
    """an index handler"""

    template = "index.html"

    @ashtml()
    def get(self):
        form = LoginForm(self.request.form)
        return self.render(form=form)
