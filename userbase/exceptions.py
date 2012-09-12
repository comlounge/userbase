__all__ = [
    'LoginFailed',
    'UserUnknown',
    'PasswordIncorrect',
]

class LoginFailed(Exception):
    """an exception raised in case the login was not possible. It contains further details on it"""

    def __init__(self, msg, user_credentials = {}):
        """initialize the exception with the message"""
        self.msg = msg
        self.user_credentials = user_credentials

class UserUnknown(LoginFailed):
    """a user was not found"""

class PasswordIncorrect(LoginFailed):
    """password was incorrect (or any other given credential)"""


