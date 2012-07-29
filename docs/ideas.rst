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






