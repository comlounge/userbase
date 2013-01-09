from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from wtforms import ValidationError
from userbase import db

__all__ = ['RegistrationHandler']

class RegistrationHandler(Handler):
    """show the registration form and process it"""

    template = "userbase/registration.html"

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
                    self.flash(cfg.messages.login_success %user)
                    url_for_params = cfg.urls.login_success
                    url = self.url_for(**url_for_params)
                    return redirect(url)
                if cfg.use_double_opt_in:
                    self.flash(cfg.messages.double_opt_in_pending %user)
                    url_for_params = cfg.urls.double_opt_in_pending
                else:
                    self.flash(cfg.messages.registration_success %user)
                    url_for_params = cfg.urls.registration_success
                url = self.url_for(**url_for_params)
                return redirect(url)
        return self.render(form = form, use_double_opt_in = cfg.use_double_opt_in)

    post = get
