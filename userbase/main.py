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
        if self.request.method == 'POST' and form.validate():
            f = form.data
            email = f['email'] 
            password = f['password'] 
            user = self.config.dbs.users.find_by_email(email)
            if user is None:
                self.flash("Email oder Passwort stimmen leider nicht!", css_class="error")
                raise self.redirect(self.url_for('index', force_external=True))
            if not user.check_pw(password):
                self.flash("Email oder Passwort stimmen leider nicht.", css_class="error")
                raise self.redirect(self.url_for('index', force_external=True))
            self.flash("Du bist jetzt eingeloggt", css_class="info")
            raise self.redirect(self.url_for('welcome', force_external=True))

        return self.render(form=form)

    post = get
