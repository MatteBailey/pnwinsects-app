pnwinsects-app
==============

Django app powering pnwinsects sites

A full history of the codebase can be found at https://github.com/huddlej/pnwmoths

Starting a new site
-------------------

* The following components must be installed in the environment in which the site will run:
  * Apache
  * Python
  * mod_wsgi
  * MySQL
  * pip package mananager
    * install the python modules found in requirements.txt in this repo
    * <code>pip install -r requirements.txt</code>
* Instructions for configuring Apache for Django can be found at https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/modwsgi/
* The site code can be installed with <code>git clone git@github.com:MatteBailey/pnwinsects-app.git</code>
* <code>settings.py</code> and <code>apache.conf</code> are specific to the installation, and should be symlinked from the parent directory
