import pytest
import re
import urlparse
from conftest import lre_string

def test_password_forgot_complete(app):
    """retrieve a new password"""
    mail = app.module_map['mail']
    c = app.test_client()

    # get pw forgot page
    rv = c.get("/users/pw_forgot")
    assert rv.status_code == 200
    
    # post our email address to it
    rv = c.post("/users/pw_forgot", data = dict(email="barfoo@example.com"), follow_redirects = True)
    assert rv.status_code == 200
    link = re.search(lre_string, mail.last_msg_txt).groups()[0]                                                         
    assert "Flash: A link to set a new password" in rv.data
    assert "to reset your password" in mail.last_msg_txt

    # get the link from the email
    parts = urlparse.urlsplit(link)
    url = "%s?%s" %(parts.path, parts.query)
    rv = c.get(url)
    assert "Flash" not in rv.data 
    rv = c.post(url, data = dict(password="trololol", password2="trololol"), follow_redirects = True)
    assert u"Flash: Your password has been changed" in rv.data 

    # now test login with the new password
    assert "userid" not in app.last_handler.session
    rv = c.post("/users/login", data = dict(username="foobar", password="trololol"), follow_redirects = True)
    assert "userid" in app.last_handler.session
    

def test_password_forgot_wrong_code(app):
    mail = app.module_map['mail']
    client = app.test_client()

    rv = client.get("/users/pw_code_enter?code=wrong", follow_redirects = True)
    assert u"Flash: We couldn't find a user with that code, please try again" in rv.data 

def test_password_forgot_wrong_email(app, client):
    mail = app.module_map['mail']

    rv = client.post("/users/pw_forgot", data = dict(email="wrong@example.com"), follow_redirects = True)
    assert u"Flash: The email address is not in our database" in rv.data 

def test_password_forgot_post_with_wrong_code(app):
    mail = app.module_map['mail']
    client = app.test_client()

    rv = client.post("/users/pw_code_enter?code=wrong", data = dict(password="trololol", password2="trololol"), follow_redirects = True)
    assert u"Flash: We couldn't find a user with that code, please try again" in rv.data 
    



