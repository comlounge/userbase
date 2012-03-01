from core import *
from paste.auth import auth_tkt


class LoginAdapter(object):
    """the login manager"""

    def __init__(self, handler, userdb):
        """initialize login manager"""
        self.handler = handler # the handler we adapt to
        self.userdb = userdb # the user database to use
        self.config = userdb.config

        # process the request and extract any login information
        self.userid = None
        self.user = None
        req = self.request = self.handler.request
        cookie_name = self.config.get("cookie_name", "u")
        self.cookie_secret = self.config.get("cookie_name", "foo0bar")
        if self.cookie_secret == "foo0bar":
            print "please configure a cookie secret in the login manager settings!"

        if req.cookies.has_key(cookie_name):
            at = req.cookies[cookie_name]
            try:
                self.timestamp, self.userid, self.roles, self.token_attribs = auth_tkt.parse_ticket(
                    self.cookie_secret, at, "127.0.0.1")
                print "yes"
            except auth_tkt.BadTicket, e:
                print "no"
                pass
        else:
            self.userid = None
            self.user = None
        if self.userid is not None:
            self.user = self.userdb.get(self.userid) 
            if self.user is None:
                self.log.error("user in token not found: %s " %self.userid)
                self.userid=None
                self.user=None

    def set_user(self, user):
        """login a user"""
        self.user = user
        self.userid = unicode(user.d._id)
        cookie_name = self.config.get("cookie_name", "u")
        ticket = auth_tkt.AuthTicket(self.cookie_secret, self.userid, "127.0.0.1")
        self.handler.response.set_cookie(cookie_name, ticket.cookie_value())
        return ticket.cookie_value()

    @property
    def logged_in(self):
        """check if somebody is logged in"""
        return self.user is not None
   
    def login(self, identifier, password):
        """try to login the user

        :param identifier: the configure identifier which defaults to the email address
        :param password: the password to use

        returns None if it hasn't worked, the User object otherwise

        TODO: raise some error so we can pass the error cause and the client can do what it thinks is right

        """

        user = self.userdb[identifier]
        if user is None:
            return None
        if not user.check_pw(password):
            return None
        self.user = user
        return user

    def redirect(self, url):
        """do the redirect while setting the login cookie if it exists"""
        if self.user is not None:
            value = self.set_user(self.user)
            cookie_name = self.config.get("cookie_name", "u")
            raise self.handler.redirect(url, cookies = {cookie_name: value})
        else:
            raise self.handler.redirect(url)

    def logout(self, msg=None, css_class="info"):
        """log the user out and redirect him to the logged_out screen 
        while displaying an optional flash message.

        :param msg: The message to pass via the flash message system
        :param css_class: The CSS class to use for this message
        """

        url = self.handler.url_for(self.config.logged_out_url)
        cookie_name = self.config.get("cookie_name", "u")
        if msg is not None:
            self.handler.flash(msg, css_class=css_class)
        raise self.handler.redirect(url, cookies = {cookie_name : "loggedout"})                                                                                                                                  
