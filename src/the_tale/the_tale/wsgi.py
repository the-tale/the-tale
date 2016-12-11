import os
import sys
import site

site.addsitedir('/home/the-tale/current/venv/lib/python3.5/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'the_tale.settings'

from django.core import wsgi

application = wsgi.get_wsgi_application()
