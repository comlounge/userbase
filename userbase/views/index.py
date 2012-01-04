from userbase.framework import Handler
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
        if self.logged_in:
            return self.render()
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
            self.flash("Hallo %s, Du bist jetzt eingeloggt" %user.d.name, css_class="info")
            cv = self.set_user(user)
            raise self.redirect(self.url_for('welcome', force_external=True), cookies={'u' : cv})

        return self.render(tmplname="login.html", form=form)

    post = get

class LogoutView(Handler):
    """perform a logout"""

    def get(self):
        """log the user out by deleting the cookie"""
        self.flash("Du bist nun ausgeloggt", css_class="info")
        raise self.redirect(self.url_for('index', force_external=True), delete_cookies=['u'])


