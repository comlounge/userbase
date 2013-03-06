from starflyer import Handler

class BaseHandler(Handler):
    """base handler for all userbase related handlers. Mostly we implement a dummy translation method which can be
    overwritten using sf-babel
    """

    def _(self, t):
        """dummy translation method"""
        return t
