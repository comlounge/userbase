from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from wtforms import ValidationError
from userbase import db
from userbase.base import BaseHandler
try:
    from sfext.babel import T
except ImportError:
    T = lambda x: x

__all__ = ['RegistrationHandler']

class RegistrationHandler(BaseHandler):
    """show the registration form and process it"""

    template = "registration.html"

    def get(self):
        """show the registration form"""
        cfg = self.module.config
        mod = self.module
        form = cfg.registration_form
        obj_class = cfg.user_class

        form = form(self.request.form, module = self.module)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user = mod.register(f, create_pw=False)
                if cfg.login_after_registration and not cfg.use_double_opt_in:
                    user = mod.login(self, force=True, **f)
                    self.flash(self._("Welcome, %(fullname)s") %user)
                    url_for_params = cfg.urls.login_success
                    url = self.url_for(**url_for_params)
                    return redirect(url)
                if cfg.use_double_opt_in:
                    self.flash(self._(u'To finish the registration process please check your email with instructions on how to activate your account.') %user)
                    url_for_params = cfg.urls.double_opt_in_pending
                else:
                    self.flash(self._(u'Your user registration has been successful') %user)
                    url_for_params = cfg.urls.registration_success
                url = self.url_for(**url_for_params)
                return redirect(url)
        return self.render(form = form, use_double_opt_in = cfg.use_double_opt_in)

    post = get
