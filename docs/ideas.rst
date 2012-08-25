=====
Ideas
=====

Feature ideas
=============

- predefined data structure and mongo connection via MongoEngine
- predefined forms for login and registration
- registration functionality with email verification
- password forgotten function
- password change 


basic structure
===============

We have a UserManager instance which handles all the data layer:

- It defines the User schema and database connection
- It defines additional login mechanisms


Then we have the FormManager which defines the render and templating stuff which you can include in your project:

- It knows which forms to use for which action
- It defines predefined templates to use
- It handles user input

The basic setup
===============

The basic setup without configuration is a very simple user setup:

- we have fullname, email and password as fields
- we login via email and password
- Registration
- login is stored in the session


The application setup
---------------------

We need to instantiate the UserManager and the FormManager. Both are attached to the app::

    app.users = setup_usermanager(UserManager(app, db, "users"), FormManager(app))

This will use the ``users`` collection in the given database. Besides that we don't use any configuration.


The login handler
-----------------

The login handler shows the form and processes the login. The login might fail and we might want to show maybe a captcha additionally. 





Example
-------

Instantiate the module in the app::

    class MyApp(Application):
        
        ...

        modules = [
            UserModule("db", "users") # usermanage and form manager in one
        ]

This will add new templates to be used to the app which we can use in a template like this::

    {% include _m/userbase/loginform %}

This could actually be some method as well which could take some parameters but might be slower. 



    



Components
==========

On the low level we have the following components:

- the user object which represents a user and whether it is activated etc. 
- some handlers which handle user login, registration, password reminders and user management. Along with that goes also forms and templates
- the login manager which binds all these things together. This automatically is the starflyer module. 

Usually a group of instances of these three levels will be grouped together as one configuration you can choose from.
You are free to create your own components though and reuse existing ones. 


The user object
---------------

The user object needs to derive from mongoengine and implement the following methods:

- ``get_id()`` has to return it's userid. This needs to be the unique field (might be different from _id, e.g. a username))
- ``is_active`` returns whether the user is activated or not
- ``is_anonymous`` returns whether this is the anonymous user or not (if logged in, return ``False``)
- ``get_verification_code()`` returns a new verification code to send out to the user for activating the account
- ``get_pw_forgotten_code()`` returns a new code to send out to the user for setting a new password


The userbase module/login manager 
----------------------------------

This class is used to integrate the whole system into your application. There are different classes provided
which have different configurations, e.g. for using the email or a username as login field.

Each login manager needs to implement the following methods:

- ``get_user()`` returns the logged in user
- ``logout()`` logs out the logged in user
- ``

Configuration
*************

All the handlers are hard coded into the login manager but you can subclass it and replace them. 







Workflows
=========

1. User registers with the site
2. System creates user and send out verification code (optional)
3. User activates account
4. User is active

ad 3: Code is wrong/timed out
3.1. System creates new code and sends it out



Issues
======

- how to generate a token which can be revoked? E.g. if the password is changed the cookie should be changed as well
- 




