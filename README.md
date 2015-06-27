pnwinsects-app
==============

Django app powering pnwinsects sites

A full history of the codebase can be found at https://github.com/huddlej/pnwmoths

Starting a new site
-------------------

* The following components must be installed in the environment in which the site will run:
  * Apache (using other server software is possible, but we have only tested with Apache)
  * Python 2.7
  * mod_wsgi
  * MySQL
  * pip package mananager
    * install the python modules found in requirements.txt in this repo
    * <code>pip install -r requirements.txt</code>
* Instructions for configuring Apache for Django can be found at https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/
* The site code can be installed with <code>git clone git@github.com:MatteBailey/pnwinsects-app.git</code>
* <code>settings.py</code> and <code>apache.conf</code> are specific to the installation, and should be symlinked from the parent directory

Example settings.py
-------------------
```
from settings_global import *
# Set path for logging configuration file.
logging.config.fileConfig(os.path.join(PROJECT_ROOT, "logging-live.conf"))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'NAME': 'pnwmoths',
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'user',
        'PASSWORD': 'password'
    }
}

SPECIES_SINGULAR = "moth"
SPECIES_PLURAL = "moths"
TEMPLATE_VARIABLES = {
    "SPECIES_SINGULAR": SPECIES_SINGULAR, 
    "SPECIES_PLURAL": SPECIES_PLURAL, 
    "GOOGLE_SEARCH": True,
    "ANALYTICS_ID": 'ID',
    "FUSION_ID": 'FUSION_ID'
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

SECRET_KEY = 'key_here'

CONTENT_ROOT = "/usr/local/www/images"

# Define local media root and url.
#
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/usr/local/www/pnwmoths/django/pnwmoths/static/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"

MEDIA_URL = "http://dev.pnwmoths.biol.wwu.edu/media/"

ADMIN_MEDIA_PREFIX = "/media/static/admin/"
STATIC_ROOT = MEDIA_ROOT + "static/"
STATIC_URL = MEDIA_URL + "static/"
```

Example apache.conf
-------------------

Your <code>apache.conf</code> file should also be symlinked into the <code>Includes/</code> directory of your apache directory.

```
# This line is needed to run modwsgi
SetEnv PYTHON_EGG_CACHE /tmp

NameVirtualHost *:80
TimeOut 2400

AddOutputFilterByType DEFLATE text/text text/html text/plain text/xml text/css application/x-javascript application/javascript

# PNW Dynamic Main Domain
<VirtualHost *:80>
	DocumentRoot /usr/local/www/pnwmoths/django/pnwmoths/static/media/
	ServerName pnwmoths.biol.wwu.edu
	ServerAlias www.pnwmoths.biol.wwu.edu

	# Django app
	WSGIDaemonProcess pnwmoths user=www group=www threads=1 inactivity-timeout=2400
	WSGIProcessGroup pnwmoths
	WSGIScriptAlias / /usr/local/www/pnwmoths/django/pnwmoths/app/django.wsgi
	<Directory /usr/local/www/pnwmoths/django/pnwmoths>
	Order deny,allow
	Allow from all
	</Directory>

	Alias /media/ /usr/local/www/pnwmoths/django/pnwmoths/static/media/
	<Directory /usr/local/www/pnwmoths/django/pnwmoths/static/media>
	AllowOverride All
	Order deny,allow
	Allow from all
	</Directory>

        Alias /media_alt/ /usr/local/www/pnwmoths/django/pnwmoths/app/static/media/
        <Directory /usr/local/www/pnwmoths/django/pnwmoths/app/static/media>
        AllowOverride All
        Order deny,allow
        Allow from all
        </Directory>
</VirtualHost>

# Expiration dates for media.
ExpiresActive on
ExpiresByType image/jpg "access plus 1 month"
ExpiresByType image/png "access plus 1 month"
ExpiresByType image/gif "access plus 1 month"
```
