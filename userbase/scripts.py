from starflyer import ScriptBase
import db

class UserManager(ScriptBase):

    def extend_parser(self):
        """extend the usermanager script with sub commands"""

        # TODO: let the respective user manager handle the sub commands
        # as only this one knows which fields are necessary
        #
        subparsers = self.parser.add_subparsers(help='sub commands help')
        self.add_parser = subparsers.add_parser('add', help='adding users')
        self.add_parser.add_argument('email', help='username')
        self.add_parser.add_argument('password', help='password')
        self.add_parser.add_argument('--fullname', dest="fullname", default="", help='the full name')

    def __call__(self):
        user = db.UserEMail(
            email=self.args.email,
            fullname=self.args.fullname,
            password=self.args.password)
        user.save()
        print "user created"




def um():
    mgr = UserManager()
    mgr()
