#encoding=utf8
import pytest
import re
import urlparse
from conftest import lre_string

def test_set_new_password(app):
    """set a new password"""
    c = app.test_client()
    
    # login to set the new password
    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"))

    # get pw forgot page
    rv = c.get("/users/pw_set")
    assert rv.status_code == 200

    rv = c.post("/users/pw_set", data = dict(password="newpass", password2="newpass"), follow_redirects=True)
    assert "Flash: Your password has been changed." in rv.data

    # try to login with new password
    rv = c.post("/users/logout", follow_redirects = True)

    # login with old password
    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"), follow_redirects = True)
    assert "Flash: Incorrect password." in rv.data
    assert "userid" not in app.last_handler.session

    # login with new password
    rv = c.post("/users/login", data = dict(username="foobar", password="newpass"), follow_redirects = True)
    assert "Flash: Hello Foo bar" in rv.data
    assert "userid" in app.last_handler.session
    
def test_set_new_password_not_logged_in(app):
    c = app.test_client()
    
    # get pw forgot page
    rv = c.get("/users/pw_set", follow_redirects=True)
    assert rv.status_code == 200
    assert "Flash: Please log in" in rv.data
    assert "userid" not in app.last_handler.session

def test_set_new_password_mismatch(app):
    c = app.test_client()
    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"), follow_redirects = True)
    rv = c.post("/users/pw_set", data = dict(password="newpass", password2="newpass2"), follow_redirects=True)
    assert "Passwords must match" in rv.data

def test_set_new_password_umlaut(app):
    c = app.test_client()
    rv = c.post("/users/login", data = dict(username="foobar", password="barfoo"), follow_redirects = True)
    rv = c.post("/users/pw_set", data = dict(password="rübe", password2="rübe"), follow_redirects=True)
    assert "Flash: Your password has been changed" in rv.data
