__all__ = [
    'LoginFailed',
    'UnknownUser',
    'IncorrectPassword',
]

class LoginFailed(Exception):
    """an exception raised in case the login was not possible. It contains further details on it"""

    def __init__(self, msg, user_credentials = {}):
        """initialize the exception with the message"""
        self.msg = msg
        self.user_credentials = user_credentials

class UnknownUser(LoginFailed):
    """a user was not found"""

class IncorrectPassword(LoginFailed):
    """password was incorrect (or any other given credential)"""


