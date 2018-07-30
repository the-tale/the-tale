
import smart_imports

smart_imports.all()


site.addsitedir('/home/the-tale/current/venv/lib/python3.5/site-packages')

os.environ['DJANGO_SETTINGS_MODULE'] = 'the_tale.settings'


application = django_wsgi.get_wsgi_application()
