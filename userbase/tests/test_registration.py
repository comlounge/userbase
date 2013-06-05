# coding=utf-8

import pytest
import re
import urlparse
from conftest import lre_string

def test_registration(client, app):
    """log in as the dummy user"""
    mail = app.module_map['mail']
    resp = client.get("/users/register")
    post_data = {
        'username'  : 'user1',
        'password'  : 'password1',
        'password2' : 'password1',
        'email'     : 'foobar@example.org',
        'fullname'  : 'Mr. Foo Bar',
    }
    resp = client.post("/users/register", data = post_data)
    assert "To finish the registration process please check your email with instructions on how to activate your account." in str(app.last_handler.session['_flashes'])
    link = re.search(lre_string, mail.last_msg_txt).groups()[0]                                                         
    assert "um Deinen Account zu aktivieren" in mail.last_msg_txt
    parts = urlparse.urlsplit(link)
    url = "%s?%s" %(parts.path, parts.query)
    resp = client.get(url)
    assert "" in str(app.last_handler.session['_flashes'])

