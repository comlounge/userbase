from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from wtforms import ValidationError
from userbase.decorators import logged_in, permission
from userbase import db
from forms import PasswordChangeForm
import datetime

__all__ = ['PasswordSetHandler']

class PasswordSetHandler(Handler):
    """send a link for setting a new password"""

    template = "pw_new.html"

    @logged_in()
    def get(self):
        """show the password set form"""
        cfg = self.module.config
        mod = self.module
        user = self.user
        form = cfg.pw_change_form(self.request.form)

        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user.password = f['password']
                user.pw_code = None
                user.save()
                self.flash(self._(u'Your password has been changed.') %user)
                url_for_params = cfg.urls.pw_set_success
                url = self.url_for(**url_for_params)
                return redirect(url)
        return self.render(form = form)
    post = get

