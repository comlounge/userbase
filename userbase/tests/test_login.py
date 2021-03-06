import pytest

def test_login(app):
    """log in as the dummy user"""
    c = app.test_client()
    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"))
    assert rv.status_code == 302
    assert "userid" in app.last_handler.session
    
    # test the handler directly
    req = app.make_request(path = "/users/login", method="POST", data = dict(username="foobar", password="barfoo"))
    handler = app.find_handler(req)
    rv = handler(**req.view_args)
    assert app.module_map.userbase.get_user(handler).username == "foobar"


def test_login_email(email_app):
    """log in as the dummy user by email"""
    app = email_app
    c = email_app.test_client()
    email_app.make_user()
    rv = c.post("/users/login", data = dict(email="barfoo@example.org", password="barfoo"))
    assert rv.status_code == 302 # 302 also means redirect and thus success, 200 might mean error
    assert "userid" in email_app.last_handler.session
    
    # test the handler directly
    req = app.make_request(path = "/users/login", method="POST", data = dict(email="barfoo@example.org", password="barfoo"))
    handler = app.find_handler(req)
    rv = handler(**req.view_args)
    assert app.module_map.userbase.get_user(handler).username == "foo_bar"

def test_login_email_lowercase(email_app):
    """log in as the dummy user by email using a non-lowercase email"""
    app = email_app
    c = email_app.test_client()
    email_app.make_user()
    rv = c.post("/users/login", data = dict(email="BarFoo@Example.org", password="barfoo"))
    assert rv.status_code == 302 # 302 also means redirect and thus success, 200 might mean error
    assert "userid" in email_app.last_handler.session

def test_login_logout(app):
    # login
    c = app.test_client()

    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"))
    assert "userid" in app.last_handler.session

    rv = c.get("/users/logout")
    assert "userid" not in app.last_handler.session

def test_no_remember_me(app):
    """check if we can delete the session cookie and still be logged in"""
    c = app.test_client()

    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"))
    assert "userid" in app.last_handler.session

    # remove session cookies 
    c.cookie_jar.clear_session_cookies()
    rv = c.get("/")
    assert "userid" not in app.last_handler.session

def test_remember_me(app):
    """check if we can delete the session cookie and still be logged in"""
    c = app.test_client()
    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo", remember=1))
    assert "userid" in app.last_handler.session
    rv = c.get("/")
    assert "userid" in app.last_handler.session
    c.cookie_jar.clear_session_cookies() # remove login
    rv = c.get("/")
    assert "userid" in app.last_handler.session


def test_logout(app):
    c = app.test_client()

    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"))
    rv = c.get("/")
    assert "userid" in app.last_handler.session
    rv = c.post("/users/logout")
    rv = c.get("/")
    assert "userid" not in app.last_handler.session

def test_logout_with_remember(app):
    c = app.test_client()

    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo", remember=1))
    rv = c.get("/")
    assert "userid" in app.last_handler.session
    rv = c.post("/users/logout")
    rv = c.get("/")
    assert "userid" not in app.last_handler.session

def test_last_login(app):
    c = app.test_client()

    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"))
    ll = app.last_handler.user.last_login

    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"))
    assert ll < app.last_handler.user.last_login
