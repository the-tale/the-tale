
import smart_imports

smart_imports.all()


class EMAILED_STATE(rels_django.DjangoEnum):
    records = (('EMAILED', 0, 'письма отправлены'),
               ('NOT_EMAILED', 1, 'письма не отправлены'),
               ('DISABLED', 2, 'отправка запрещена'))
