from starflyer import Handler as BaseHandler
import starflyer
import werkzeug

class Handler(BaseHandler):

    @starflyer.ashtml()
    def get(self):
        return self.render()

    def prepare_render(self, params):
        """provide more information to the render method"""
        params = super(Handler, self).prepare_render(params)
        params.is_logged_in = False
        params.user_id = None
        params.session_id = None
        params.user = None
        params.txt = self.settings.texts
        return params


