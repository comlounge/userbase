from usermanager.db import User, Users, InvalidData, ObjectNotFound
import pytest
import pymongo

def test_basics(users):

    data = {'email': "mrtopf@gmail.com", 'name': "Christian", 'password': "foobar", '_id': "27628762"}
    user = User(data)
    assert user.d.email == "mrtopf@gmail.com"

    user = users.put(user)
    user2 = users.get(user.d._id)
    assert user2.d.email == "mrtopf@gmail.com"

def test_notfound(users):
    pytest.raises(ObjectNotFound, users.get, 0)

def test_invalid():

    data = {'email' : "mrtopf", 'name' : "Christian", 'password' : "foobar", '_id' : "27628762"}
    user = User(data)
    pytest.raises(InvalidData, user.serialize)
    try:
        user.serialize()
    except InvalidData, e:
        e.errors == {'email': u'Invalid email address'}

def test_registration_flow(users):

    data = {'email' : "mrtopf@gmail.com", 'name':"Christian"}
    user = User(data)
    user.set_pw("foobar")
    user = users.put(user)
    user.send_validation_code()
    user = users.put(user)

    recs = users.all
    assert recs.count == 1

