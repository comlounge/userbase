from starflyer import Application, asjson, ashtml
from werkzeug.routing import Map, Rule, NotFound, RequestRedirect
from framework import Handler

import werkzeug.wsgi
import os

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
    settings = setup.setup(**local_conf)
    app = App(settings)
    app = werkzeug.wsgi.SharedDataMiddleware(app, {
        '/css': os.path.join(settings.static_file_path, 'css'),
        '/js': os.path.join(settings.static_file_path, 'js'),
        '/img': os.path.join(settings.static_file_path, 'img'),
    })
    return app



