
import smart_imports

smart_imports.all()


class MESSAGE_STATE(rels_django.DjangoEnum):
    records = (('WAITING', 1, 'ожидает обработки'),
               ('PROCESSED', 2, 'обработано'),
               ('ERROR', 3, 'ошибка при обработке'),
               ('SKIPPED', 4, 'сервис не отправляет этот тип сообщений'))
