from starflyer import ScriptBase
import db

class UserManager(ScriptBase):

    def extend_parser(self):
        """extend the usermanager script with sub commands"""

        # TODO: let the respective user manager handle the sub commands
        # as only this one knows which fields are necessary
        #
        subparsers = self.parser.add_subparsers(help='sub commands help', dest="cmd")
        self.add_parser = subparsers.add_parser('add', help='adding users')
        self.add_parser.add_argument('username', help='username')
        self.add_parser.add_argument('email', help='email address')
        self.add_parser.add_argument('password', help='password')
        self.add_parser.add_argument('--fullname', dest="fullname", default="", help='the full name')

        self.add_parser = subparsers.add_parser('pw', help='set password for a user')
        self.add_parser.add_argument('username', help='username')
        self.add_parser.add_argument('password', help='password')

        self.add_parser = subparsers.add_parser('permissions', help='set permissions for a user')
        self.add_parser.add_argument('username', help='username')
        self.add_parser.add_argument('permissions', help='comma-separated list of permissions')

    def __call__(self):
        m = self.app.module_map['userbase']
        data = vars(self.args)
        del data['config_file']
        if data['cmd'] == "add":
            user = m.users()
            user.update(data)
            user.save()
            user.activate()
            user.save()
        elif data['cmd'] == "pw":
            user = m.get_user_by_username(data['username'])
            user.password = data['password']
            user.pw_code = None
            user.save()
        elif data['cmd'] == "permissions":
            user = m.get_user_by_username(data['username'])
            permissions = data['permissions'].split(",")
            permissions = [perm.strip() for perm in permissions]
            user.permissions = permissions
            user.save()
        
def um():
    mgr = UserManager()
    mgr()
