# coding=utf-8
from starflyer import Module, Application, Handler, URL
from userbase import username_userbase, email_userbase
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
        'server_name'   : "127.0.0.1",
        'session_cookie_domain' : "127.0.0.1",
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

class UserbaseEMailTestApp(Application):
    """base app for testing"""

    defaults = {
        'secret_key'    : "182827",
        'testing'       : True,
        'debug'         : True,
        'secret_key'    : "f00bar",
        'server_name'   : "127.0.0.1",
        'session_cookie_domain' : "127.0.0.1",
    }

    routes = [
        URL("/", "root", TestHandler)
    ]

    modules = [
        mail_module(debug = True),
        email_userbase(
            url_prefix = "/users",
            login_after_registration    = True,
            double_opt_in               = True,
            enable_registration         = True,
            mongodb_name = DB_NAME,
            login_success_url_params = {'endpoint' : 'root'},
            logout_success_url_params = {'endpoint' : 'root'},
        ),
    ]

    def make_user(self):
        """make dummy user"""
        ub = self.module_map['userbase']
        user = ub.register({
            "password"      : "barfoo", 
            "email"         : "barfoo@example.org", 
            "fullname"      : "Foo bar",
        }, force = True, create_pw = False)


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
    return app

@pytest.fixture
def email_app(request, db):
    """create the simplest app with uploader support ever"""
    return UserbaseEMailTestApp(__name__)

@pytest.fixture
def email_client(request, email_app):
    return werkzeug.Client(email_app, werkzeug.BaseResponse)


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
