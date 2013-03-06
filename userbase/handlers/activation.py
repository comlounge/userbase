from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from wtforms import ValidationError
from userbase import db
from ..base import BaseHandler

__all__ = ['ActivationHandler', 'ActivationCodeHandler']

class ActivationHandler(BaseHandler):
    """perform the activation process"""

    template = "_m/userbase/activation.html"

    def get(self):
        """show the registration form"""
        cfg = self.module.config
        mod = self.module
        code = self.request.args.get("code", None)
        if self.request.method == 'POST':
            code = self.request.form.get("code", "")
        else:
            code = self.request.args.get("code", None)
        if code is not None:
            # TODO: check expiration time
            user = mod.get_user_by_activation_code(code)
            if user is not None:
                user.activate()
                mod.login(self, user=user, save = False)
                user.save()
                self.flash(cfg.messages.activation_success %user)
                url_for_params = cfg.urls.activation_success
                url = self.url_for(**url_for_params)
                return redirect(url)
            else:
                url = self.url_for(endpoint=".activation_code")
                params = {'url': url, 'code' : code}
                self.flash(self._("""The activation code is not valid. Please try again or click <a href="%(url)s">here</a> to get a new one.""") %params, category="danger")
        return self.render()

    post = get


class EMailForm(Form):
    """form for asking for an email address to send the code to"""
    email       = TextField('E-Mail', [validators.Length(max=200), validators.Email(), validators.Required()],
        description = "Please enter the email address you registered with to receive a new activation code."
    )

class ActivationCodeHandler(Handler):
    """send out a new activation code in case a user is not yet activated and we have a valid email address"""

    template = "_m/userbase/send_activation_code.html"

    def get(self):
        """show the registration form"""
        cfg = self.module.config
        mod = self.module
        form = EMailForm(self.request.form)

        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user = mod.get_user_by_email(f['email'])
                if user is not None:
                    # send out new activation code and redirect to code sent success screen 
                    if user.active:
                        self.flash(cfg.messages.already_active %user)
                        url_for_params = cfg.urls.activation_success
                        url = self.url_for(**url_for_params)
                        return redirect(url)
                    mod.send_activation_code(user)
                    self.flash(cfg.messages.activation_code_sent %user)
                    url_for_params = cfg.urls.activation_code_sent
                    url = self.url_for(**url_for_params)
                    return redirect(url)
                else:
                    self.flash(cfg.messages.email_unknown, category="danger")
        return self.render(form = form)
    post = get
