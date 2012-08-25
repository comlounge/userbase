from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, validators
from userbase import db

__all__ = ['EMailLoginForm', 'EMailLoginHandler']


class EMailLoginForm(Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email()])
    password    = PasswordField('Password', [validators.Length(min=5, max=35)])

class UsernameLoginForm(Form):
    username    = TextField('Username', [validators.Length(max=200), validators.Required()])
    password    = PasswordField('Password', [validators.Length(min=1, max=35), validators.Required()])

class EMailLoginHandler(Handler):
    """show the user login form and process it"""

    template = "_m/userbase/login_email.html"

    def get(self):
        """show the login form"""
        form = EMailLoginForm(self.request.form)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                email = f['email']
                password = f['password']

                # try ot retrieve the user
                user = self.module.config.user_obj.objects.get(email = email)
                if user is not None:
                    if user.check_password(password):
                        url_for_params = self.module.config.login_success_url_params
                        url = self.url_for(**url_for_params)
                        self.session['user'] = user.id
                        self.flash("Welcome, %s" %user.fullname)
                        return redirect(url)
            self.flash("Login failed", category="danger")
        return self.render(form = form)

    post = get
