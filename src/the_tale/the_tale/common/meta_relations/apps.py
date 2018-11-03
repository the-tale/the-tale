
import smart_imports

smart_imports.all()


class Config(django_apps.AppConfig):
    name = 'the_tale.common.meta_relations'
    label = 'dext_meta_relations'
    verbose_name = 'meta relations'

    def ready(self):
        from . import logic
        logic.autodiscover_relations()
        logic.autodiscover_types()
