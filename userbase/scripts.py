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
        self.add_parser.add_argument('username', help='username')
        self.add_parser.add_argument('email', help='email address')
        self.add_parser.add_argument('password', help='password')
        self.add_parser.add_argument('--fullname', dest="fullname", default="", help='the full name')

    def __call__(self):
        m = self.app.module_map['userbase']
        data = vars(self.args)
        del data['config_file']
        user = m.users()
        print 1
        user.update(data)
        print 2
        user.save()
        print "user created"
        print user




def um():
    mgr = UserManager()
    mgr()
