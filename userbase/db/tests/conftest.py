from userbase.db import User, Users
import pymongo

def pytest_funcarg__db(request):
    """return a database object"""
    conn = pymongo.Connection()
    db = conn.usermanager_testdatabase
    return db

def pytest_funcarg__users(request):
    """return a database object"""
    db = request.getfuncargvalue("db")
    db.users.remove()
    return Users(db.users)

