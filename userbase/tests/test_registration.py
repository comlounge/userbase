# coding=utf-8

import pytest
import re
import urlparse
from conftest import lre_string

def test_registration(app):
    """log in as the dummy user"""
    mail = app.module_map['mail']
    client = app.test_client()

    # get the registration form
    resp = client.get("/users/register")
    post_data = {
        'username'  : 'user1',
        'password'  : 'password1',
        'password2' : 'password1',
        'email'     : 'foobar@example.org',
        'fullname'  : 'Mr. Foo Bar',
    }

    # post registration data to that form
    rv = client.post("/users/register", data = post_data, follow_redirects = True)
    assert "Flash: To finish the registration process please check your email with instructions on how to activate your account." in rv.data
    link = re.search(lre_string, mail.last_msg_txt).groups()[0]                                                         
    assert "in order to activate your account" in mail.last_msg_txt

    # follow the activation link
    parts = urlparse.urlsplit(link)
    url = "%s?%s" %(parts.path, parts.query)
    rv = client.get(url, follow_redirects=True)
    assert "Flash: Your account has been successfully activated." in rv.data


def test_email_lowercase_on_registration(email_app):
    mail = email_app.module_map['mail']
    client = email_app.test_client()

    resp = client.get("/users/register")
    post_data = {
        'username'  : 'user1',
        'password'  : 'password1',
        'password2' : 'password1',
        'email'     : 'FooBar@ExamPle.org',
        'fullname'  : 'Foo Bar',
    }
    rv = client.post("/users/register", data = post_data, follow_redirects = True)

    # activate user
    link = re.search(lre_string, mail.last_msg_txt).groups()[0]
    parts = urlparse.urlsplit(link)
    url = "%s?%s" %(parts.path, parts.query)
    rv = client.get(url, follow_redirects=True)

    # try to login with email
    req = email_app.make_request(path = "/users/login", method="POST", data = dict(email="FooBar@ExamPle.org", password="password1"))
    handler = email_app.find_handler(req)
    rv = handler(**req.view_args)
    assert email_app.module_map.userbase.get_user(handler).username == "foo_bar"

    # use different case on email
    req = email_app.make_request(path = "/users/login", method="POST", data = dict(email="foobar@example.org", password="password1"))
    handler = email_app.find_handler(req)
    rv = handler(**req.view_args)
    assert email_app.module_map.userbase.get_user(handler).username == "foo_bar"



def test_email_registration_double_username(email_app):
    """test if the username derived from the fullname is unique"""
    app = email_app
    mail = app.module_map['mail']
    client = app.test_client()

    def reg_user(email):
        """register and activate a user with the given email"""

        resp = client.get("/users/register")
        post_data = {
            'password'  : 'password1',
            'password2' : 'password1',
            'email'     : email,
            'fullname'  : 'Foo Bar',
        }
        rv = client.post("/users/register", data = post_data, follow_redirects = True)

        # activate user
        link = re.search(lre_string, mail.last_msg_txt).groups()[0]
        parts = urlparse.urlsplit(link)
        url = "%s?%s" %(parts.path, parts.query)
        rv = client.get(url, follow_redirects=True)

    reg_user('foobar1@example.org')
    reg_user('foobar2@example.org')
    reg_user('foobar3@example.org')

    # check the 2 accounts for usernames
    req = email_app.make_request(path = "/users/login", method="POST", data = dict(email="foobar1@example.org", password="password1"))
    handler = email_app.find_handler(req)
    rv = handler(**req.view_args)
    assert email_app.module_map.userbase.get_user(handler).username == "foo_bar"

    req = email_app.make_request(path = "/users/login", method="POST", data = dict(email="foobar2@example.org", password="password1"))
    handler = email_app.find_handler(req)
    rv = handler(**req.view_args)
    assert email_app.module_map.userbase.get_user(handler).username == "foo_bar_1"

    req = email_app.make_request(path = "/users/login", method="POST", data = dict(email="foobar3@example.org", password="password1"))
    handler = email_app.find_handler(req)
    rv = handler(**req.view_args)
    assert email_app.module_map.userbase.get_user(handler).username == "foo_bar_2"


def test_registration_wrong_activation_code(client, app):
    """log in as the dummy user"""
    mail = app.module_map['mail']

    # post registration data to that form
    post_data = {
        'username'  : 'user1',
        'password'  : 'password1',
        'password2' : 'password1',
        'email'     : 'foobar@example.org',
        'fullname'  : 'Mr. Foo Bar',
    }
    rv = client.post("/users/register", data = post_data, follow_redirects = True)
    url = "/users/activate?code=wrong_code"
    rv = client.get(url, follow_redirects=True)
    assert "Flash: The activation code is not valid." in rv.data

def test_registration_double_email(client, app):
    post_data = {
        'username'  : 'user1',
        'password'  : 'password1',
        'password2' : 'password1',
        'email'     : 'barfoo@example.com',
        'fullname'  : 'Mr. Foo Bar',
    }
    rv = client.post("/users/register", data = post_data, follow_redirects = True)
    assert "this email address is already taken" in rv.data
    
def test_registration_double_username(client, app):
    post_data = {
        'username'  : u'foobar',
        'password'  : 'password1',
        'password2' : 'password1',
        'email'     : 'barfoo2@example.com',
        'fullname'  : 'Mr. Foo Bar',
    }
    rv = client.post("/users/register", data = post_data, follow_redirects = True)
    assert "this username is already taken" in rv.data
    
