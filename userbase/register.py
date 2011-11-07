from starflyer import Application, asjson, ashtml
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from framework import Handler
import werkzeug.wsgi
import os
from db import User

import setup

from wtforms import Form, TextField, validators, TextAreaField, PasswordField

class RegistrationForm(Form):
    name        = TextField('Ihr Name', [validators.Length(min=6, max=35)])
    email       = TextField('Ihre Email-Adresse', [validators.Length(min=6, max=35), validators.Email()])
    password    = PasswordField('Passwort', [validators.Length(min=6, max=35)])
    password2   = PasswordField('Passwort Wiederholung', [validators.Length(min=6, max=35)])
    bio         = TextAreaField('Bio (optional)')


class RegistrationView(Handler):
    """an index handler"""

    template = "registration.html"

    @ashtml()
    def get(self):
        """show the registration form"""

        # TODO: check if user exists via WTForms
        # TODO: send validation mail
        # TODO: add updated and created and workflow state
        form = RegistrationForm(self.request.form)
        if self.request.method == 'POST' and form.validate():       
            # TODO: check email availability in db model or widget validator?
            if self.config.dbs.users.by_email(form.email.data) is not None:
                return ""
            user = User(form.data, collection = self.config.dbs.users)
            user.set_pw(form.password.data)
            user = self.config.dbs.users.put(user)
            user.send_validation_code()
            user = self.config.dbs.users.put(user)
            raise self.redirect(self.url_for('registered'))
        return self.render(form=form)

    post = get


class ValidationView(Handler):
    """validate data from the registration form via AJAX"""

    @asjson()
    def get(self):
        args = self.request.values
        if "email" in args:
            email = args['email']
            if self.config.dbs.users.by_email(email) is not None:
                return "Diese E-Mail-Adresse ist schon registriert."
        return True

class RegisteredView(Handler):
    """an index handler"""

    template = "registered.html"

class ValidationCodeView(Handler):
    """view used to validate a validation code. The following can happen:

    - the code is invalid. Then it is said so and the user can optionally
      send the code again by being redirected to ValidationRetryView.
    - the code is valid. In this case the user is activated and redirected to the
      welcome screen. This screen is blank per default but can be overridden by
      the host service to show an appropriate screen.
    """

    template = "registered.html"

    def get(self, code=None):
        """validate the code"""
        print code
        # get the user for this code
        user = self.config.dbs.users.find_by_code(code)
        if user is None: # code is invalid
            return self.render(tmplname="invalid_code.html")
        user.state = "live"
        user.save()
        self.redirect(self.url_for("welcome"))




