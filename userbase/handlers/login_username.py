from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, validators
from userbase import db
from mongoengine import Q

__all__ = ['UsernameLoginHandler', 'UsernameLoginForm']

class UsernameLoginForm(Form):
    username    = TextField('Username', [validators.Length(max=200), validators.Required()])
    password    = PasswordField('Password', [validators.Length(min=1, max=35), validators.Required()])

class UsernameLoginHandler(Handler):
    """show the user login form and process it"""

    template = "_m/userbase/login_username.html"

    def get(self):
        """show the login form"""
        form = UsernameLoginForm(self.request.form)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                username = f['username']
                password = f['password']

                # try ot retrieve the user
                users = self.module.config.user_obj.objects(Q(username = username), class_check = False)
                if len(users) > 0:
                    user = users[0]
                    if user.check_password(password):
                        url_for_params = self.module.config.login_success_url_params
                        url = self.url_for(**url_for_params)
                        self.session['user'] = user.id
                        self.flash("Welcome, %s" %user.fullname)
                        return redirect(url)
            self.flash("Login failed", category="danger")
        return self.render(form = form)

    post = get
