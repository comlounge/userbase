from starflyer import Module, Application, Handler, URL
from userbase import username_userbase
import py.path
import pymongo
import datetime
from bson.objectid import ObjectId

DB_NAME = "userbase_testing_cbsjszcg8cs7tsc"

class TestHandler(Handler):
    
    def get(self):
        return "ok"

class MyApp(Application):
    """test app with uploader"""

    defaults = {
        'secret_key'    : "182827",
        'testing'       : True
    }
    routes = [
        URL("/", "root", TestHandler)
    ]
    modules = [
        username_userbase(
            mongodb_name = DB_NAME,
            login_success_url_params = {'endpoint' : 'root'},
            logout_success_url_params = {'endpoint' : 'root'},
        ),
    ]

def setup_db():
    db = pymongo.Connection()[DB_NAME]
    db.users.insert({ "_id" : u"foobar", 
        "username": u"foobar", 
        "pw" : "96948aad3fcae80c08a35c9b5958cd89", 
        "email" : "barfoo@example.com", 
        "fullname": "Foo bar",
        "last_ip": "",
        "last_login": None,
        "activation_time": None,
        "activation_code_expires": None,
        "activation_code": None,
        "password_code": None,
        "password_code_expires": None,
        "active": True,
        'date_creation' : datetime.datetime.utcnow()})
    return db

def teardown_db(db):
    pymongo.Connection()[DB_NAME].users.remove()

def pytest_funcarg__db(request):
    return request.cached_setup(
        setup = setup_db,
        teardown = teardown_db,
        scope = "module")

def pytest_funcarg__app(request):
    """create the simplest app with uploader support ever"""
    db = request.getfuncargvalue("db")
    return request.cached_setup(
        setup = lambda: MyApp(__name__),
        scope = "module")


