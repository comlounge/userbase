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
