
import smart_imports

smart_imports.all()


class Config(django_apps.AppConfig):
    name = 'the_tale.common.utils'
    label = 'the_tale_utils'
    verbose_name = 'The-Tale utils'
