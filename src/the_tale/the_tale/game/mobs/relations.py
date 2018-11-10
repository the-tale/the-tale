
import smart_imports

smart_imports.all()


class MOB_RECORD_STATE(rels_django.DjangoEnum):
    records = (('ENABLED', 0, 'в игре'),
               ('DISABLED', 1, 'вне игры'))


class INDEX_ORDER_TYPE(rels_django.DjangoEnum):
    records = (('BY_LEVEL', 'by_level', 'по уровню'),
               ('BY_NAME', 'by_name', 'по имени'))
