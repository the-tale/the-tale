
import smart_imports

smart_imports.all()


class Config(django_apps.AppConfig):
    name = 'the_tale.game.chronicle'
    label = 'chronicle'
    verbose_name = 'chronicle'

    def ready(self):
        from . import signal_processors
        pass
