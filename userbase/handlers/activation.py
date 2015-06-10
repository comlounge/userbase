from starflyer import Handler, redirect
from userbase import db
from ..base import BaseHandler
from forms import ActivationEMailForm

__all__ = ['ActivationHandler', 'ActivationCodeHandler']

class ActivationHandler(BaseHandler):
    """perform the activation process"""

    template = "activation.html"

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
                self.flash(self._("Your account has been successfully activated.") %user)
                url_for_params = cfg.urls.activation_success
                url = self.url_for(**url_for_params)
                return redirect(url)
            else:
                url = self.url_for(endpoint=".activation_code")
                params = {'url': url, 'code' : code}
                self.flash(self._("""The activation code is not valid. Please try again or click <a href="%(url)s">here</a> to get a new one.""") %params, category="danger")
        return self.render()

    post = get

class ActivationCodeHandler(Handler):
    """send out a new activation code in case a user is not yet activated and we have a valid email address"""

    template = "send_activation_code.html"

    def get(self):
        """show the registration form"""
        cfg = self.module.config
        mod = self.module
        form = ActivationEMailForm(self.request.form)

        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user = mod.get_user_by_email(f['email'])
                if user is not None:
                    # send out new activation code and redirect to code sent success screen 
                    if user.active:
                        self.flash(self._("The user is already active. Please log in.") %user)
                        url_for_params = cfg.urls.activation_success
                        url = self.url_for(**url_for_params)
                        return redirect(url)
                    mod.send_activation_code(user)
                    self.flash(self._("A new activation code has been sent out, please check your email") %user)
                    url_for_params = cfg.urls.activation_code_sent
                    url = self.url_for(**url_for_params)
                    return redirect(url)
                else:
                    self.flash(self._("This email address cannot not be found in our user database"), category="danger")
        return self.render(form = form)
    post = get
