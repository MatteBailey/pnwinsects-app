#!/usr/local/bin/python3

import os, sys
sys.path.append('/usr/local/www/pnwmoths/django')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
