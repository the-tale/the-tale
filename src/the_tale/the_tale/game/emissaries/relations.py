
import smart_imports

smart_imports.all()


class STATE(rels_django.DjangoEnum):
    records = (('IN_GAME', 1, 'Работает'),
               ('OUT_GAME', 2, 'Вне игры'))


class REMOVE_REASON(rels_django.DjangoEnum):
    records = (('NOT_REMOVED', 0, 'Не удалён'),
               ('KILLED', 1, 'Убит'),
               ('DISMISSED', 2, 'Уволен'))
