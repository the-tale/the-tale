
import smart_imports

smart_imports.all()


class ACCESS_TOKEN_STATE(rels_django.DjangoEnum):
    records = (('UNPROCESSED', 0, 'неизвестен'),
               ('ACCEPTED', 1, 'разрешено'))


class AUTHORISATION_STATE(rels_django.DjangoEnum):
    records = (('NOT_REQUESTED', 0, 'авторизация не запрашивалась'),
               ('UNPROCESSED', 1, 'пользователь ещё не принял решение'),
               ('ACCEPTED', 2, 'авторизация прошла успешно'),
               ('REJECTED', 3, 'в авторизации отказано'))
