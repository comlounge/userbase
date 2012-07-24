"""

login handlers

"""

import starflyer

__all__=['LoginView', 'LogoutView']

class LoginView(starflyer.Handler):
    """handler just for logging a user in"""

    def post(self):
        """try to login the user"""
        lm = self.login_manager
        form = lm.login_form(self.request.form, config=self.config)
        if self.request.method == 'POST' and form.validate():
            f = form.data
            email = f['email']
            password = f['password']
            user = self.login_manager.login(email, password)
            if user is not None:
                self.flash("Welcome, %s" %user.d.name, css_class="info")
            else:
                self.flash("Login failed", css_class="danger")
                raise self.redirect(self.url_for("index"))
        else:
            self.flash("Login fehlgeschlagen", css_class="danger")
            raise self.redirect(self.url_for("index"))
        raise self.login_manager.redirect(self.url_for('index'))



class LogoutView(starflyer.Handler):
    """handler just for logging a user in"""

    def get(self):
        """log the user out"""
        self.login_manager.logout("You have been logged out.", "success")

