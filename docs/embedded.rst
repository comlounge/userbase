=============
Embedded Mode
=============

This mode is used in case you want to use the usermanager inside your own application.
In this case you have to provide all the handlers and urls yourself but will call the
functions of the usermanager like you would a library.

Screens
=======

The following screens are needed:

- login screen (shows the form and processes the input, will redirect on success and show the form again on failture)
- registration screen (shows the form, will redirect with message after successful registration)
- submission of validation code (this is the URL which will be sent in the email for activating your account. this might simply redirect but if the code is wrong you should be redirected to the screen to send it again)
- resending of a validation code (here you have to enter your email address and will get the validation code sent again)
- password forgotten (here you enter your email address and will get an email with a code to reset your password)
- password new screen (this is the link the email links to. Here you have a form to set a new password. It will redirect with a message in case of success).
- password change form (here you can change your password)
- profile change form (here you can change your profile)
