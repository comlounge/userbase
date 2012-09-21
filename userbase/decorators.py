import werkzeug
import functools
import json
import datetime
from werkzeug.utils import redirect

__all__ = ['logged_in', 'permission']

class logged_in(object):
    """check if a valid user is present"""

    def __call__(self, method):
        """check user"""
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            if self.user is None:
                self.flash('Please log in.', category="danger")
                return redirect(self.url_for("userbase.login", force_external=True))
            return method(self, *args, **kwargs)
        return wrapper

class permission(object):
    """check if the logged in user has the correct permission to use that
    method"""

    def __init__(self, *required):
        """initialize this decorator with a list of permissions from
        which the logged in user needs at least one to be able to
        perform this method"""
        self.required = set(required)

    def __call__(self, method):

        that = self
        required = set([p.lower() for p in self.required])

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            # is everybody allowed? (makes no sense to use this decorator but anyway)
            if 'everybody' in required:
                return method(self, *args, **kwargs)

            # no user object means we cannot check and thus it's unauthed
            if self.user is None:
                raise werkzeug.exceptions.Unauthorized()

            # retrieve the permissions for the user via the corresponding hook
            mod = self.app.module_map['userbase']
            has_permissions = set(mod.hooks.get_permissions_for_user(self.user, handler = self))
            
            if has_permissions.isdisjoint(required):
                raise werkzeug.exceptions.Unauthorized()

            return method(self, *args, **kwargs)
        return wrapper

