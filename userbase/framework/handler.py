from starflyer import Handler as BaseHandler
from paste.auth import auth_tkt
import starflyer
import werkzeug

class Handler(BaseHandler):

    def prepare(self):
        """check user etc."""

        self.userid = None
        self.user = None
        if self.request.cookies.has_key("u"):
            at = self.request.cookies['u']
            try:
                self.timestamp, self.userid, self.roles, self.token_attribs = auth_tkt.parse_ticket(
                    self.config.settings.cookie_secret, at, "127.0.0.1")
                self.log.debug("found user %s in cookie" %self.userid)
            except auth_tkt.BadTicket, e:
                self.log.error("BAD token detected: %s " %e)
                pass
        else:
            self.userid = None
            self.user = None
        if self.userid is not None:
            self.user = self.config.dbs.users[self.userid]
            if self.user is None:
                self.log.error("user in token not found: %s " %self.userid)
                self.userid=None
                self.user=None
        # TODO: set an empty cookie and redirect to homepage on errors

    @starflyer.ashtml()
    def get(self):
        return self.render()

    def prepare_render(self, params):
        """provide more information to the render method"""
        params = super(Handler, self).prepare_render(params)
        params.is_logged_in = False
        params.user_id = None
        params.session_id = None
        params.user = None
        params.txt = self.config.i18n.de
        return params

    def set_user(self, user):                                                                                                                                           
        """store a user in a cookie"""
        self.user = user
        self.userid = unicode(user.d['_id'])
        ticket = auth_tkt.AuthTicket(self.config.settings.cookie_secret, self.userid, "127.0.0.1")
        self.response.set_cookie("u", ticket.cookie_value())
        return ticket.cookie_value()

    @property
    def logged_in(self):
        """return True if user is logged in otherwise False"""
        return self.user is not None

    def logout(self):                                                                                                                   
        """log a user out by deleting the cookie"""
        self.response.delete_cookie("u")      
    
