
import smart_imports

smart_imports.all()


class PATH_DIRECTION(rels_django.DjangoEnum):
    records = (('LEFT', 'l', 'лево'),
               ('RIGHT', 'r', 'право'),
               ('UP', 'u', 'верх'),
               ('DOWN', 'd', 'низ'))
