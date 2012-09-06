from starflyer import Module, Application, Handler, URL
from userbase import username_userbase
import mongoengine
import py.path
import pymongo

class TestHandler(Handler):
    
    def get(self):
        return "ok"

def pytest_funcarg__app(request):
    """create the simplest app with uploader support ever"""

    db_name = "userbase_testing_cbsjszcg8cs7tsc"
    pymongo.Connection().drop_database(db_name)
    mongoengine.connect(db=db_name) # hopefully nobody uses this
    # TODO: make test config configurable

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

    app = MyApp(__name__)

    # create a user
    m = app.module_map['userbase']
    uo = m.config.user_class
    data = {
        'username' : 'foobar',
        'password' : 'barfoo',
        'email'    : 'barfoo@example.com',
        'fullname' : 'Foo Baz'
    }
    user = uo(**data)
    user.save()

    return app





