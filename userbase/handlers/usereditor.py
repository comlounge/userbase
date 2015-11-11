from starflyer import Handler, redirect
from wtforms import ValidationError
import itertools
from userbase import db
from userbase.decorators import logged_in, permission
import werkzeug.exceptions

__all__ = ['UserList', 'UserEdit', 'UserAdd', 'UserActivate', 'SendPW']

class UserAdapter(object):
    """extend the user with some additional attributes we compute via module and handler"""

    def __init__(self, userbase, user):
        self.userbase = userbase
        self.user = user
    
    @property
    def id(self):
        return str(self.user._id)

    @property
    def readable_permissions(self):
        """return permissions in a readable format"""
        perms = self.userbase.config.permissions
        return "<br>".join([str(perms.get(p, "n/a")) for p in self.user.permissions])

class UserWrapper(object):
    """class for producing wrapped users by being some funky iterator"""

    def __init__(self, userbase, users):
        """initialize the class with the list of base db users and the userbase module"""
        self.users = users
        self.userbase = userbase

    def __iter__(self):
        for user in self.users:
            yield UserAdapter(self.userbase, user)

class UserList(Handler):
    """show the list of users"""

    template = "editor/list.html"

    @logged_in()
    @permission("userbase:admin")
    def get(self):
        """show the user list"""
        mod = self.module
        users = self.module.users.find()
        return self.render(users = UserWrapper(mod, users))

class UserEdit(Handler):
    """edit a user"""

    template = "editor/edit.html"

    @logged_in()
    @permission("userbase:admin")
    def get(self, uid=None):
        """show the user list"""
        cfg = self.module.config
        mod = self.module
        user = mod.get_user_by_id(uid)
        if user is None:
            raise werkzeug.exceptions.NotFound()

        form = cfg.edit_form(self.request.form, obj = user, module = self.module)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user.update(**f)
                user.save()
                self.flash(self._(u'user data has been updated') %user)
                url = self.url_for("userbase.userlist")
                return redirect(url)
        return self.render(form = form)

    post = get

class UserAdd(Handler):
    """add a user"""

    template = "editor/add.html"

    @logged_in()
    @permission("userbase:admin")
    def get(self):
        """show the user list"""
        cfg = self.module.config
        mod = self.module

        form = cfg.add_form(self.request.form, module = self.module)
        if self.request.method == 'POST':
            if form.validate():
                f = form.data
                user = mod.register(f, force = True, create_pw = True)
                user.update(**f)
                user.save()
                # TODO: send password and user info 
                self.flash(self._(u'A new user has been added') %user)
                url = self.url_for("userbase.userlist")
                return redirect(url)
        return self.render(form = form)

    post = get

class UserActivate(Handler):
    """activate or deactivate a user"""

    @logged_in()
    @permission("userbase:admin")
    def post(self, uid = None):
        """depending on the old state you either activate or deactivate a user here. It's a toggle."""
        cfg = self.module.config
        mod = self.module
        user = mod.get_user_by_id(uid)
        if user is None:
            raise werkzeug.exceptions.NotFound()
        user.active = not user.active
        user.save()
        if user.active:
            self.flash(self._(u'The user has been activated') %user)
        else:
            self.flash(self._(u'The user has been deactivated') %user)
        url = self.url_for("userbase.userlist")
        return redirect(url)

class SendPW(Handler):
    """send a password reset link to a user"""

    @logged_in()
    @permission("userbase:admin")
    def post(self, uid = None):
        """set the pw forgotten link"""
        cfg = self.module.config
        mod = self.module
        user = mod.get_user_by_id(uid)

        # send out the password reset link
        mod.send_pw_code(user)
        self.flash(self._(u'A link for resetting the password has been sent to the user') %user)

        url = self.url_for("userbase.userlist")
        return redirect(url)

