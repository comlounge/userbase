from starflyer import Handler, redirect
from wtforms import Form, TextField, PasswordField, BooleanField, validators
from wtforms import ValidationError
from userbase import db
from forms import PWEMailForm
import datetime

__all__ = ['PasswordForgotHandler', 'PasswordSetHandler', 'PasswordCodeHandler']

class PasswordSetHandler(Handler):
    """send a link for setting a new password"""

    template = "pw_set.html"

    def get(self):
        """show the password set form"""
        cfg = self.module.config
        mod = self.module
        code = self.request.args.get("code", None)
        if self.request.method == 'POST':
            code = self.request.form.get("code", "")
        else:
            code = self.request.args.get("code", None)
        if code is not None:
            user = mod.get_user_by_activation_code(code)
            if user is not None:
                user.activate()
                mod.login(self, user=user, save = False)
                user.save()
                self.flash(self._("Your password has been successfully changed"))
                url_for_params = cfg.urls.activation_success
                url = self.url_for(**url_for_params)
                return redirect(url)
            else:
                url = self.url_for(endpoint=".activation_code")
                params = {'url': url, 'code' : code}
                self.flash(self._("Your password change has failed" %params), category="danger")
                self.flash(cfg.messages.activation_failed %params, category="danger")
        return self.render()

    post = get


class PasswordForgotHandler(Handler):
    """send out a pw forgotten link in case a user has forgotten his password"""

    template = "send_pw_code.html"

    def get(self):
        """show the form for entering your email address. The form can be overwritten in the userbase module"""
        cfg = self.module.config
        mod = self.module
        form = cfg.pw_forgot_form(self.request.form)

        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user = mod.get_user_by_email(f['email'])
                if user is not None:

                    # send out pw forgot code and redirect to code sent success screen 
                    mod.send_pw_code(user)
                    self.flash(self._(u'A link to set a new password has been sent to you') %user)
                    url_for_params = cfg.urls.pw_code_success
                    url = self.url_for(**url_for_params)
                    return redirect(url)
                else:
                    self.flash(self._(u'The email address is not in our database.'))
        return self.render(form = form)
    post = get

class PasswordCodeHandler(Handler):
    """verify the given password code and if ok, allow user to enter a new password"""

    template = "pw_new.html"

    def get(self):
        """show the form for entering a new password."""
        cfg = self.module.config
        mod = self.module

        # check pw code which comes via URL
        code = self.request.args.get("code", None)
        if code is None:
            self.flash("The URL is missing a code for the password reset. Please enter the email address you registered with to receive a proper link", 
                category="danger")
            url = self.url_for("userbase.pw_forgot")
            return redirect(url)

        user = mod.get_user_by_pw_code(code)
        if user is None:
            self.flash("We couldn't find a user with that code, please try again", category="danger")
            url = self.url_for("userbase.pw_forgot")
            return redirect(url)

        # check for expiration time
        if user.pw_code_expires < datetime.datetime.now():
            self.flash("The code has expired, please try again", category="danger")
            url = self.url_for("userbase.pw_forgot")
            return redirect(url)

        form = cfg.pw_change_form(self.request.form)

        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                # send out pw forgot code and redirect to code sent success screen 
                user.password = f['password']
                user.pw_code = None
                user.save()
                self.flash(self._(u'Your password has been changed') %user)
                url_for_params = cfg.urls.pw_code_success
                url = self.url_for(**url_for_params)
                return redirect(url)
        return self.render(form = form, code = code)
    post = get
