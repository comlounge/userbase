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
import main
import register

def setup(**kw):
    """setup the application. 

    :param kw: optional keyword arguments to override certain values of the 
        settings section of the configuration

    :return: a configuration object to be passed into the application
    """

    config = starflyer.Configuration()
    config.register_sections('dbs', 'logs', 'mail', 'i18n')
    config.register_snippet_names('header', 'footer')
    config.register_template_chains("main", "emails")

    ## various constants
    config.update_settings({
        #'log_name' : "participate",
        'virtual_host' : "http://localhost:8222",
        'virtual_path' : "/",
        'title' : "Usermanager",
        'description' : "a usermanager",
        'mongodb_name' : "usermanager",
        'mongodb_port' : 27017,
        'mongodb_host' : "localhost",
        'cookie_secret' : "czcds7z878cdsgsdhcdjsbhccscsc87csds76876ds",
        'session_cookie_name' : "s",
        'message_cookie_name' : "m",
        'from_addr' : "noreply@example.org"
    })
    config.update_settings(kw) # update with data from ini file

    ## routing
    config.routes.extend([
        ('/', 'index', main.IndexView),
        ('/registered', 'registered', register.RegisteredView),
        ('/register', 'register', register.RegistrationView),
        ('/register/validate', 'register.validate', register.ValidationView),
        ('/validate/<code>', 'validate', register.ValidationCodeView),
    ])

    ## databases
    config.dbs.db = pymongo.Connection(
        config.settings.mongodb_host,
        config.settings.mongodb_port
    )[config.settings.mongodb_name]
    config.dbs.users = db.Users(config.dbs.db.users, config=config)

    ## templates
    config.templates.main.append(PackageLoader("userbase","templates"))
    config.templates.emails.append(PackageLoader("userbase", "emails"))


    # configure text contents 
    # TODO: make this really i18n, also in starflyer
    fp = pkg_resources.resource_stream(__name__, 'text.ini')
    config.i18n.de = yaml.load(fp)                                                                                                                    
    config.i18n._default = "de"

    ## static resources like JS, CSS, images
    static_file_path = pkg_resources.resource_filename(__name__, 'static')
    config.register_static_path("/css", os.path.join(static_file_path, 'css'))
    config.register_static_path("/js", os.path.join(static_file_path, 'js'))
    config.register_static_path("/img", os.path.join(static_file_path, 'img'))

    ## setup events
    config.events.register("starflyer.config.finalize:after", after_config_finalize)

    return config

def after_config_finalize(name, config, **kw):
    """triggers in the coniguration finalization phase"""
    #server = smtplib.SMTP()
    server = postmeister.DummyServer(printout=True)
    config.mail.mailer = postmeister.MailAPI(server, 
        from_addr = config.settings.from_addr, 
        templates = config.templates.emails)

