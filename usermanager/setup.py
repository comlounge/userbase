import pkg_resources
import pymongo
import starflyer
import yaml
import smtplib
import postmeister

from jinja2 import Environment, PackageLoader, PrefixLoader
from logbook import Logger

import db

def setup(**kw):
    """initialize the setup"""
    settings = starflyer.AttributeMapper()

    settings.log_name = "participate"
    settings.static_file_path = pkg_resources.resource_filename(__name__, 'static')
    settings.mongodb_name = "usermanager"
    settings.mongodb_port = 27017
    settings.mongodb_host = "localhost"

    # cookie related
    # TODO: add expiration dates, domains etc. maybe make it a dict?
    settings.cookie_secret = "czcds7z878cdsgsdhcdjsbhccscsc87csds76876ds"
    settings.session_cookie_name = "s"
    settings.message_cookie_name = "m"

    ####################################################################
    settings.update(kw)
    ####################################################################

    settings.db = pymongo.Connection(
        settings.mongodb_host,
        settings.mongodb_port
    )[settings.mongodb_name]
    settings.db_users = db.Users(settings.db.users)
    settings.log = Logger(settings.log_name)

    settings.templates = Environment(loader=PrefixLoader({
        "framework" : PackageLoader("starflyer","templates"),
        "master" : PackageLoader("usermanager","templates"),
    }))

    email_templates = PackageLoader("usermanager", "emails")
    server = smtplib.SMTP()
    settings.mailer = postmeister.MailAPI(server, from_addr = "noreply@comlounge.net", loader = email_templates)

    # read text constants
    #
    fp = pkg_resources.resource_stream(__name__, 'text.ini')
    settings.texts = yaml.load(fp)                                                                                                                    

    return settings

