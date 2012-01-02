from userbase.db import User, Users, InvalidData, ObjectNotFound
import pytest
import pymongo
import datetime

def test_basics(users):

    data = {'email': "mrtopf@gmail.com", 'name': "Christian", 'password': "foobar", '_id': "27628762", 'username':'mrtopf'}
    user = User(data)
    assert user.d.email == "mrtopf@gmail.com"

    user = users.put(user)
    user2 = users.get(user.d._id)
    assert user2.d.email == "mrtopf@gmail.com"

def test_notfound(users):
    pytest.raises(ObjectNotFound, users.get, 0)

def test_invalid():

    data = {'email' : "mrtopf", 'name' : "Christian", 'password' : "foobar", '_id' : "27628762", 'username':'mrtopf'}
    user = User(data)
    pytest.raises(InvalidData, user.serialize)
    try:
        user.serialize()
    except InvalidData, e:
        e.errors == {'email': u'Invalid email address'}

def test_registration_flow(users):

    data = {'email' : "mrtopf@gmail.com", 'name':"Christian", 'username' : 'mrtopf'}
    user = User(data)
    user.set_pw("foobar")
    user = users.put(user)
    #user.send_validation_code()
    user = users.put(user)

    recs = users.all
    assert recs.count == 1

def test_load_and_save(users):
    data = {'email' : "mrtopf@gmail.com", 'name':"Christian", 'username' : 'mrtopf'}
    user = User(data)
    user.set_pw("foobar")
    user = users.put(user)

    # retrieve it again
    user = users.get(user.d._id)
    user.d.state = "code_sent"
    mydate = user.d.validation_code_sent = datetime.datetime.now()

    user = users.put(user)

    user = users.get(user.d._id)
    assert user.d.state == "code_sent"
    assert user.d.validation_code_sent.timetuple() == mydate.timetuple()

