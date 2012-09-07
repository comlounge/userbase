from starflyer import Module, Application, Handler, URL
from userbase import username_userbase
import mongoengine
import py.path
import pymongo
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
            login_success_url_params = {'endpoint' : 'root'},
            logout_success_url_params = {'endpoint' : 'root'},
        ),
    ]

def setup_db():
    mongoengine.connect(db=DB_NAME) # hopefully nobody uses this
    db = pymongo.Connection()[DB_NAME]
    db.users.insert({ "_id" : ObjectId("5049c63707afeda89a000002"), "username" : "foobar", "_types" : [ "UserUsername" ], "pw" : "96948aad3fcae80c08a35c9b5958cd89", "_cls" : "UserUsername", "fullname" : "Foo Baz", "email" : "barfoo@example.com" })
    return db

def teardown_db(db):
    #pymongo.Connection().drop_database(DB_NAME)
    pymongo.Connection()[DB_NAME].users.remove()
    #db.users.insert({ "_id" : ObjectId("5049c63707afeda89a000002"), "username" : "foobar", "_types" : [ "UserUsername" ], "pw" : "96948aad3fcae80c08a35c9b5958cd89", "_cls" : "UserUsername", "fullname" : "Foo Baz", "email" : "barfoo@example.com" })

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





