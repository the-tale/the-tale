
import smart_imports

smart_imports.all()


settings = utils_app_settings.app_settings('XSOLLA',
                                           SECRET_KEY='secret_key',
                                           ALLOWED_IPS=('127.0.0.1', 'testserver', 'localhost'))
