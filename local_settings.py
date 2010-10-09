
## For debugging, you can use this:
# EMAIL_HOST = 'localhost'
# EMAIL_PORT = '1025'
#
# And you'll get the emails in the console executing:
# python -m smtpd -n -c DebuggingServer localhost:1025

# Or you can use the console email backend if you are using django >= 1.2:
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
