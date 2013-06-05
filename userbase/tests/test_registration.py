# coding=utf-8

import pytest
import re
import urlparse
from conftest import lre_string

def test_registration(client, app):
    """log in as the dummy user"""
    mail = app.module_map['mail']

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
    
