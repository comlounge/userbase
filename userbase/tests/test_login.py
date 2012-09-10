import pytest

def test_login(app):
    """log in as the dummy user"""
    c = app.test_client()
    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo"))
    assert rv.status_code == 302
    assert "userid" in app.last_handler.session

    # test the handler directly
    req = app.make_request(path = "/userbase/login", method="POST", data = dict(username="foobar", password="barfoo"))
    handler = app.find_handler(req)
    rv = handler(**req.view_args)
    assert app.module_map.userbase.get_user(handler).username == "foobar"

def test_login_logout(app):
    # login
    c = app.test_client()

    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo"))
    assert "userid" in app.last_handler.session

    rv = c.get("/userbase/logout")
    assert "userid" not in app.last_handler.session

def test_no_remember_me(app):
    """check if we can delete the session cookie and still be logged in"""
    c = app.test_client()

    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo"))
    assert "userid" in app.last_handler.session

    # remove session cookies 
    c.cookie_jar.clear_session_cookies()
    rv = c.get("/")
    assert "userid" not in app.last_handler.session

def test_remember_me(app):
    """check if we can delete the session cookie and still be logged in"""
    c = app.test_client()

    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo", remember=1))
    assert "userid" in app.last_handler.session
    rv = c.get("/")
    assert "userid" in app.last_handler.session
    c.cookie_jar.clear_session_cookies() # remove login
    rv = c.get("/")
    assert "userid" in app.last_handler.session


def test_logout(app):
    c = app.test_client()

    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo"))
    rv = c.get("/")
    assert "userid" in app.last_handler.session
    rv = c.post("/userbase/logout")
    rv = c.get("/")
    assert "userid" not in app.last_handler.session

def test_logout_with_remember(app):
    c = app.test_client()

    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo", remember=1))
    rv = c.get("/")
    assert "userid" in app.last_handler.session
    rv = c.post("/userbase/logout")
    rv = c.get("/")
    assert "userid" not in app.last_handler.session

def test_last_login(app):
    c = app.test_client()

    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo"))
    ll = app.last_handler.user.last_login

    rv = c.post("/userbase/login", data = dict(username="foobar", password="barfoo"))
    assert ll < app.last_handler.user.last_login
