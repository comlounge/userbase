from starflyer import Application, asjson, ashtml
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from framework import Handler

import werkzeug.wsgi

import setup
import register

class IndexView(Handler):
    """an index handler"""

    template = "master/index.html"

class WTal2011(Handler):
    """an index handler"""

    template = "master/wtal2011.html"


class App(Application):

    def setup_handlers(self, map):
        """setup the mapper"""
        self.add_rule('/', 'index', IndexView)
        self.add_rule('/registered', 'registered', register.RegisteredView)
        self.add_rule('/register', 'register', register.RegistrationView)
        self.add_rule('/register/validate', 'register.validate', register.ValidationView)

def app_factory(**local_conf):
    config = setup.setup(**local_conf)
    app = App(config)
    return werkzeug.wsgi.SharedDataMiddleware(app, config._static_map)



