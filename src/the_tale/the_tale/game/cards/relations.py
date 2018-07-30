
import smart_imports

smart_imports.all()


class RARITY(rels_django.DjangoEnum):
    priority = rels.Column()
    short_text = rels.Column()

    records = (('COMMON', 0, 'обычная карта', 3**4, 'обычная'),
               ('UNCOMMON', 1, 'необычная карта', 3**3, 'необычная'),
               ('RARE', 2, 'редкая карта', 3**2, 'редкая'),
               ('EPIC', 3, 'эпическая карта', 3**1, 'эпическая'),
               ('LEGENDARY', 4, 'легендарная карта', 3**0, 'легендарная'))


class AVAILABILITY(rels_django.DjangoEnum):
    records = (('FOR_ALL', 0, 'для всех'),
               ('FOR_PREMIUMS', 1, 'только для подписчиков'))


class COMBINED_CARD_RESULT(rels_django.DjangoEnum):
    records = (('NO_CARDS', 0, 'Нечего превращать'),
               ('EQUAL_RARITY_REQUIRED', 1, 'Карты должны быть одной редкости'),
               ('DUPLICATE_IDS', 2, 'Попытка передать одну карту как две'),
               ('COMBINE_1_COMMON', 3, 'Нельзя превращать одну обычную карту'),
               ('COMBINE_3_LEGENDARY', 4, 'Нельзя превращать три легендарные карты'),
               ('SUCCESS', 5, 'Карты превращены успешно'),
               ('TOO_MANY_CARDS', 6, 'Вы пытаетесь объединить слишком много карт'))


class STORAGE(rels_django.DjangoEnum):
    records = (('FAST', 0, 'колода быстрого доступа'),
               ('ARCHIVE', 1, 'хранилище редко используемых карт'),
               ('NEW', 2, 'новые карты'))
