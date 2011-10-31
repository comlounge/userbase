import pkg_resources
import pymongo
import yaml
import smtplib
import os
import starflyer

import postmeister

from jinja2 import Environment, PackageLoader, PrefixLoader
from logbook import Logger
import db

class UsermanagerConfiguration(starflyer.Configuration):
    """special configurator instance for usermanager with defaults"""
    sections = ['dbs', 'logs', 'mail', 'i18n']
    defaults = {
        'log_name' : "participate",
        'mongodb_name' : "usermanager",
        'mongodb_port' : 27017,
        'mongodb_host' : "localhost",
        'cookie_secret' : "czcds7z878cdsgsdhcdjsbhccscsc87csds76876ds",
        'session_cookie_name' : "s",
        'message_cookie_name' : "m",
        'from_addr' : "noreply@example.org"
    }

def setup(**kw):
    """setup the application. 

    :param kw: optional keyword arguments to override certain values of the 
        settings section of the configuration

    :return: a configuration object to be passed into the application
    """

    config = UsermanagerConfiguration()
    config.update_settings(kw)
    config.dbs.db = pymongo.Connection(
        config.settings.mongodb_host,
        config.settings.mongodb_port
    )[config.settings.mongodb_name]
    config.dbs.users = db.Users(config.dbs.db.users)

    config.logs.log = Logger(config.settings.log_name)

    config.templates.main = Environment(loader=PackageLoader("usermanager","templates"))
    config.templates.emails = email_templates = PackageLoader("usermanager", "emails")

    server = smtplib.SMTP()
    config.mail.mailer = postmeister.MailAPI(server, from_addr = config.settings.from_addr, loader = email_templates)

    # configure text contents 
    # TODO: make this really i18n, also in starflyer
    fp = pkg_resources.resource_stream(__name__, 'text.ini')
    config.i18n.de = yaml.load(fp)                                                                                                                    
    config.i18n._default = "de"

    # configure static file paths for this package
    static_file_path = pkg_resources.resource_filename(__name__, 'static')
    config.register_static_path("/css", os.path.join(static_file_path, 'css'))
    config.register_static_path("/js", os.path.join(static_file_path, 'js'))
    config.register_static_path("/img", os.path.join(static_file_path, 'img'))

    return config

def setup2(**kw):
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

