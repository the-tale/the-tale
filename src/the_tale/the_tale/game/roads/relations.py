
import smart_imports

smart_imports.all()


class PATH_DIRECTION(rels_django.DjangoEnum):
    reversed = rels.Column()

    records = (('LEFT', 'l', 'лево', 'r'),
               ('RIGHT', 'r', 'право', 'l'),
               ('UP', 'u', 'верх', 'd'),
               ('DOWN', 'd', 'низ', 'u'))


class ROAD_PATH_ERRORS(rels_django.DjangoEnum):
    records = (('NO_ERRORS', 0, 'Нет ошибок'),
               ('PASS_THROUGH_BUILDING', 1, 'Дорога не должна проходить через клетку со зданием'),
               ('NO_START_PLACE', 2, 'Догора должна начинаться в городе'),
               ('NO_FINISH_PLACE', 3, 'Дорога должна заканчиваться в городе'),
               ('PASS_THROUGH_PLACE', 4, 'Дорога не должна проходить через клетку с городом'),
               ('CELL_NOT_ON_MAP', 5, 'Дорога не должна выходить за границы карты'),
               ('HAS_CYCLES', 6, 'В пути не должно быть петель'),
               ('WRONG_FORMAT', 7, 'Описание пути содержит недопустимые символы'))
