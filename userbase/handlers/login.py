from starflyer import Handler
from wtforms import Form, TextField, PasswordField, validators
from userbase import db

class LoginFormEMail(Form):
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email()])
    password    = PasswordField('Password', [validators.Length(min=5, max=35)])

class LoginWithEMail(Handler):
    """show the user login form and process it"""

    template = "_m/userbase/login_email.html"

    def get(self):
        """show the login form"""
        form = LoginFormEMail(self.request.form)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user = db.UserEMail(**f)
                print user
                user.save()
                return "ok"
                email = f['email']
                password = f['password']
                user = self.login_manager.login(email, password)
                if user is not None:
                    url = self.url_for("index", _id=0)
                    self.flash("Welcome, %s" %user.d.fullname, category="info")
                    print "success"
                    return self.login_manager.redirect(url)
                else:
                    print "failed"
                    self.flash("Login failed", category="danger")
            else:
                self.flash("Login failed", category="danger")
        return self.render(form = form)

    post = get
