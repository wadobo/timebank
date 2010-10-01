# -*- coding: utf-8 -*- 
# Django settings for bdt1 project.
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

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('tim', 'ti@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'bdt1'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 'mysql.1984.lsi'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-es'

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
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'k#)-9d^v+^k37nt_j0%9+mdvlq5qj%_1@^-d&!m()w^sfvfdj&'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'bdt.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	"/var/www/django/templates",
)

INSTALLED_APPS = (
    'django.contrib.auth',
	'django.contrib.humanize', #añadido
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
	'django.contrib.admin',
	'bdt.aplicacion',
	'bdt.serv',
	# 'django.contrib.databrowse',
)

# Más cosas

# la página de inicio o '/' es la página donde se hará login
LOGIN_URL = '/bdt'
#Se debe pasar como parametro

# una vez hecho login se redirigirá a la página personal
LOGIN_REDIRECT_URL = 'personal/'

# Esto es porque la información con la que se almacena un usuario por defecto no es suficiente, definimos otro modelo perfilusuario
AUTH_PROFILE_MODULE = 'aplicacion.perfilusuario'

#La ruta para servir documentos estáticos (básicamente los css).
STATIC_DOC_ROOT = '/var/www/django/site_media'


DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y, H:i'
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
SESSION_COOKIE_AGE=6000 #900 15 min. sin actividad expira la sesión, en la siguienta acción se redirige a login.

#TEMPLATE_STRING_IF_INVALID="Invalid:%s" #Muestra el mensaje + el nombre del objeto inválido

EMAIL_HOST = 'mail.us.es'
EMAIL_PORT = 25
EMAIL_HOST_USER = '1984lsi'
EMAIL_HOST_PASSWORD = 'email-1984-use'
