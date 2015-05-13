# coding=utf-8
from starflyer import Module, Application, Handler, URL
from userbase import username_userbase
from sfext.mail import mail_module
import py.path
import pytest
import werkzeug
import pymongo
import datetime
from bson.objectid import ObjectId
from sfext.mail import mail_module

DB_NAME = "userbase_testing_cbsjszcg8cs7tsc"

class TestHandler(Handler):

    template = "index.html"
    
    def get(self):
        return self.render()

class UserbaseTestApp(Application):
    """base app for testing"""

    defaults = {
        'secret_key'    : "182827",
        'testing'       : True,
        'debug'         : True,
        'secret_key'    : "f00bar",
        'server_name'   : "dev.localhost",
        'session_cookie_domain' : "dev.localhost",
    }

    routes = [
        URL("/", "root", TestHandler)
    ]

    modules = [
        mail_module(debug = True),
        username_userbase(
            url_prefix = "/users",
            login_after_registration    = True,
            double_opt_in               = True,
            enable_registration         = True,
            mongodb_name = DB_NAME,
            login_success_url_params = {'endpoint' : 'root'},
            logout_success_url_params = {'endpoint' : 'root'},
        ),
    ]

@pytest.fixture
def db(request): 
    db = pymongo.MongoClient()[DB_NAME]
    def fin():
        db.users.remove()
    request.addfinalizer(fin)
    return db

@pytest.fixture
def app(request, db):
    """create the simplest app with uploader support ever"""
    app = UserbaseTestApp(__name__)
    ub = app.module_map['userbase']
    user = ub.register({
        "username"      : u"foobar", 
        "password"      : "barfoo", 
        "email"         : "barfoo@example.com", 
        "fullname"      : "Foo bar",
    }, force = True, create_pw = False)
    print user._id
    return app

@pytest.fixture
def client(request, app):
    return werkzeug.Client(app, werkzeug.BaseResponse)

import re
pattern = """
(
  (?:
    https?://
    |
    www\d{0,3}[.]
    |
    [a-z0-9.\-]+[.][a-z]{2,4}/
  )
  (?:
    [^\s()<>]+
    |
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)
  )+
  (?:
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)
    |
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]
  )
)
"""
pattern = "".join([p.strip() for p in pattern.split()])
lre_string = re.compile(pattern, re.S|re.M|re.I)                                                                        
