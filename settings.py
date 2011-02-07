# -*- coding: utf-8 -*-
# Django settings for timebank project.
# Copyright (C) 2009 Tim Gaggstatter <Tim.Gaggstatter AT gmx DOT net>
# Copyright (C) 2010 Eduardo Robles Elvira <edulix AT gmail DOT com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
from django.utils.translation import ugettext_lazy as _

curdir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# To remove timebank.fcgi from urls
FORCE_SCRIPT_NAME = ""

SITE_NAME="Timebank"

ADMINS = (
    ('admin', 'admin@localhost'),
)

DEFAULT_FROM_EMAIL="admin@localhost"

OWNERS = MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'

# Database name or path to database file if using sqlite3.
DATABASE_NAME = 'database.sqlite'

# Not used with sqlite3.
DATABASE_USER = ''
DATABASE_PASSWORD = ''

# Set to empty string for localhost. Not used with sqlite3.
DATABASE_HOST = ''
DATABASE_PORT = ''

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
# Automatically when executing python manage.py start-project
SECRET_KEY = 'k#)-9d^v+^k37nt_j0%9+mdvlq5qj%_1@^-d&!m()w^sfvfdj&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware'
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'main.context_processor.base',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or
    # "C:/www/django/templates". Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(curdir, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.humanize',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'serv',
    'main',
    'flashmsg',
    'news',
    'tinymce',
    'south',
    'user',
    'globaltags',
    'messages',
    'djangoratings',
    'tasks',
    'rosetta'
)

LOGIN_URL = '/'

# The URL where requests are redirected after login when the
# contrib.auth.login view gets no next parameter.
LOGIN_REDIRECT_URL = '/'

# Path for static docs (css, images, etc)
STATIC_DOC_ROOT = os.path.join(curdir, 'site_media')

DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y, H:i'
SESSION_EXPIRE_AT_BROWSER_CLOSE=True

AUTHENTICATION_BACKENDS = (
    'user.auth_backends.CustomUserModelBackend',
)
CUSTOM_USER_MODEL = 'user.Profile'

# reCAPTCHA fill in local_settings.py, not here
RECAPTCHA_PUBLIC_KEY = ""
RECAPTCHA_PRIVATE_KEY = ""

# Email configuration. Configure appropiately if emails are not directly sent by localhost
#EMAIL_HOST = ''
#EMAIL_PORT = 0
#EMAIL_HOST_USER = ''
#EMAIL_HOST_PASSWORD = ''

MIN_CREDIT = -10*60
MAX_CREDIT = 20*60
MAX_CREDITS_PER_TRANSFER = 10*60


LANGUAGES = (
      ('es', _('Spanish')),
      ('es_ng', _('Spanish (neutral gender)')),
      ('en', _('English'))
)

# Just in case
RATINGS_VOTES_PER_IP = 3
AUTOACCEPT_REGISTRATION=False

SHOW_CAPTCHAS=True

try:
    from local_settings import *
except ImportError:
    pass
