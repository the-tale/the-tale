
import smart_imports

smart_imports.all()


class Config(django_apps.AppConfig):
    name = 'the_tale.common.postponed_tasks'
    label = 'postponed_tasks'
    verbose_name = 'postponed_tasks'

    def ready(self):
        from . import prototypes
        prototypes.autodiscover()
