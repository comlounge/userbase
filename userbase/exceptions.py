__all__ = [
    'LoginFailed',
    'RegistrationFailed',
    'UserUnknown',
    'PasswordIncorrect',
    'UserNotActive',
]

class LoginFailed(Exception):
    """an exception raised in case the login was not possible. It contains further details on it"""

    def __init__(self, msg, user_credentials = {}, user = None):
        """initialize the exception with the message"""
        self.msg = msg
        self.user_credentials = user_credentials
        self.user = user

class RegistrationFailed(Exception):
    """an exception raised in case the user registration has failed for some reason. It contains further details on it"""
    def __init__(self, msg, user_data = {}):
        """initialize the exception"""
        self.msg = msg
        self.user_data = user_data

class UserUnknown(LoginFailed):
    """a user was not found"""

class PasswordIncorrect(LoginFailed):
    """password was incorrect (or any other given credential)"""

class UserNotActive(LoginFailed):
    """the user was not yet activated"""


