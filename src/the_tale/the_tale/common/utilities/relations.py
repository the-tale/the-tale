
import smart_imports

smart_imports.all()


class STATE(rels_django.DjangoEnum):
    records = (('WAITING', 0, 'ожидает'),
               ('RUNNING', 1, 'работает'),
               ('FINISHED', 2, 'завершена'))


class RESULT(rels_django.DjangoEnum):
    records = (('SUCCESS', 0, 'успех'),
               ('ERROR', 1, 'ошибка'),
               ('SKIPPED', 2, 'пропущена'),
               ('GAME_MUST_BE_RUNNING', 3, 'игра должна быть запущена'),
               ('GAME_MUST_BE_STOPPED', 4, 'игра должна быть остановлена'),
               ('GAME_MUST_BE_IN_DEBUG', 5, 'игра должна быть в режиме отладки'))
