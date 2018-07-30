
import smart_imports

smart_imports.all()


class POST_STATE(rels_django.DjangoEnum):
    records = (('NOT_MODERATED', 0, 'не проверен'),
               ('ACCEPTED', 1, 'принят'),
               ('DECLINED', 2, 'отклонён'), )
