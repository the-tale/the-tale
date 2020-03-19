
import smart_imports

smart_imports.all()


class STATE(rels_django.DjangoEnum):
    records = (('REQUESTED', 0, 'запрошен'),
               ('ACTIVE', 1, 'активен'))
