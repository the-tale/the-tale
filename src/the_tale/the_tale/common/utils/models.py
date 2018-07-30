
import smart_imports

smart_imports.all()


class UUIDField(django_models.CharField):

    def __init__(self, *argv, **kwargs):
        kwargs['max_length'] = 36
        super(UUIDField, self).__init__(*argv, **kwargs)
