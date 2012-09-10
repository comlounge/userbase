from starflyer import Handler
import datetime
from werkzeug.contrib.securecookie import SecureCookie

__all__ = ['UserbaseHandlerMixin', 'UserbaseHandler']

class UserbaseHandlerMixin(object):
    """additional methods for using in userbase handlers for managing
    users and cookies
    """

    ###
    ### user handling
    ###

    def login(self, user, remember= False):
        """log the user in by user object. This does not verification but only sets cookies and such"""
        self.session['userid'] = user.id

        if remember:    
            payload = {
                'userid' : user.id,
                'hash'   : user.get_token(),
            }
            self._save_cookie(payload)

    def logout(self):
        """forget about a user"""
        del self.session['userid']


    ###
    ### cookie handling
    ###

    def _save_cookie(self, data):
        """create a cookie and mark it for saving"""
        config = self.module.config
        app = self.app
        cookie_name = config.cookie_name
        expires = datetime.datetime.utcnow() + config.cookie_lifetime
        self.set_cookie(config.cookie_name, 
            data, 
            expires = expires, 
            secret_key = self.app.config.secret_key)

    def _load_cookie(self):
        """load a cookie from the response"""
        config = self.module.config
        cookie_name = config.cookie_name
        secret = config.secret_key
        if secret is None:
            raise RuntimeError('the user cookie is unavailable because no secret ' 
                    'key was set.  Set the secret_key on the '
                    'userbase module to something unique and secret.')
        return SecureCookie.load_cookie(self.request, cookie_name, secret_key=key)

    def _delete_cookie(self, response):
        """delete the remember cookie from the response"""
        config = self.module.config
        cookie_name = config.cookie_name
        domain = config.cookie_domain
        if domain is None:
            domain = self.app.config.session_cookie_domain
        response.delete_cookie(cookie_name, domain=domain)

    def remember_user(self, user, response):
        """remember a user"""
        if not user.is_active():
            return
        userid = user.get_id()
        token = user.get_auth_token()

class UserbaseHandler(Handler, UserbaseHandlerMixin):
    """base handler for userbase handlers implementing the userbase cookie interface"""



