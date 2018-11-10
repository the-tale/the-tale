
import smart_imports

smart_imports.all()


class BATTLE_1X1_RESULT(rels_django.DjangoEnum):
    records = (('UNKNOWN', 0, 'неизвестен'),
               ('VICTORY', 1, 'победа'),
               ('DEFEAT', 2, 'поражение'),
               ('DRAW', 3, 'ничья'))


class BATTLE_1X1_STATE(rels_django.DjangoEnum):
    records = (('WAITING', 1, 'в очереди'),
               ('PREPAIRING', 2, 'подготовка'),
               ('PROCESSING', 3, 'идёт бой'))
