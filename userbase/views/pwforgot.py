#encoding=utf8
from userbase.framework import Handler
from starflyer import ashtml

from wtforms import Form, TextField, validators, PasswordField

class EMailForm(Form):
    email       = TextField('Email-Adresse:', [validators.Length(min=6, max=35), validators.Email()])

class PasswordForm(Form):
    password    = PasswordField('Passwort', [validators.Length(min=6, max=35)])
    password2   = PasswordField('Passwort Wiederholung', [validators.Length(min=6, max=35)])

class PWForgottenView(Handler):

    template = "pwforgot.html"

    @ashtml()
    def get(self):
        form = EMailForm(self.request.form)
        if self.request.method == 'POST' and form.validate():
            f = form.data
            email = f['email'] 
            user = self.config.dbs.users.find_by_email(email)
            if user is None:
                self.flash("Leider ist uns kein Benutzer mit dieser E-Mail-Adresse bekannt!", css_class="error")
                raise self.redirect(self.url_for('pw_forgot', force_external=True))
            user.send_pw_forgotten_code(self.url_for)
            user = self.config.dbs.users.put(user)
            self.flash(u"Anleitung versendet.", description=u"Wir haben Dir per Mail eine Anleitung geschickt, mit der Du Dein Passwort zurücksetzen kannst. Bitte folge den Schritten dort.", css_class="success")
            raise self.redirect(self.url_for("index"))

        return self.render(form=form)

    post = get

class PWValidationView(Handler):
    """view used to validate a password code. The following can happen:
    """

    template = "pw_new.html"

    @ashtml()
    def get(self, code=None):
        """validate the code"""
        # get the user for this code
        # TODO: check state, delete code
        user = self.config.dbs.users.find_by_pwcode(code)
        if user is None: # code is invalid
            self.flash("Leider haben wir keinen Benutzer zu diesem Code gefunden. Fordern Sie bitte erneut einen Code an.", css_class="error")
            raise self.redirect(self.url_for("pw_forgot"))
        form = PasswordForm(self.request.form)
        if self.request.method == 'POST' and form.validate():       
            user.set_pw(form.password.data)
            user.d.pw_code = ""
            user.d.pw_code_sent = None
            user = self.config.dbs.users.put(user)
            self.flash(u"Neues Passwort gesetzt.", description=u"Du kannst Dich jetzt mit Deinem neuen Passwort einloggen.", css_class="success")
            raise self.redirect(self.url_for("index"))
        return self.render(pw_code = code, form = form)

    post = get

