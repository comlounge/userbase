__all__ = [
    'LoginFailed',
    'RegistrationFailed',
    'UserUnknown',
    'PasswordIncorrect',
    'UserNotActive',
]

class UserbaseError(Exception):
    """master class for all userbase related exceptions"""

class LoginFailed(UserbaseError):
    """an exception raised in case the login was not possible. It contains further details on it"""

    def __init__(self, msg, user_credentials = {}, username = None, user = None):
        """initialize the exception with the message

        :param user_credentials: the complete form data, usually username/email and password
        :param username: only the identifying user credential, e.g. username or email depending on config
        :param user: the user object if available
        """
        self.msg = msg
        self.user_credentials = user_credentials
        self.username = username
        self.user = user

class RegistrationFailed(UserbaseError):
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


