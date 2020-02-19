
import smart_imports

smart_imports.all()


class ACTOR_TYPE(rels_django.DjangoEnum):
    records = (('PERSON', 0, 'житель'),
               ('PLACE', 1, 'место'),
               ('MONEY_SPENDING', 2, 'трата денег'))


class DONOTHING_TYPE(rels_django.DjangoEnum):
    duration = rels.Column(unique=False)
    messages_probability = rels.Column(unique=False)

    records = (('DRUNK_SONG', 'drunk_song', 'пьяная песня', 6, 0.3),
               ('STAGGER_STREETS', 'stagger_streets', 'шляться по улицам', 10, 0.3),
               ('CHATTING', 'chatting', 'общение с друзьями', 5, 0.3),
               ('SEARCH_OLD_FRIENDS', 'search_old_friends', 'поиск старых друзей', 7, 0.3),
               ('REMEMBER_NAMES', 'remember_names', 'вспоминание имён', 3, 0.3),
               ('SPEAK_WITH_GURU', 'speak_with_guru', 'общение с гуру', 5, 0.1),
               ('STAGGER_HOLY_STREETS', 'stagger_holy_streets', 'бродить по святым улицам', 5, 0.1))


class QUEST_TYPE(rels_django.DjangoEnum):
    records = (('NORMAL', 0, 'обычный'),
               ('CHARACTER', 1, 'характерный'),
               ('UNIQUE', 2, 'уникальный'))


class QUESTS(rels_django.DjangoEnum):
    quest_class = rels.Column()
    quest_type = rels.Column(unique=False)
    priority = rels.Column(unique=False)
    allowed_for_cards = rels.Column(unique=False)

    records = (('SPYING', 0, 'шпионаж', questgen_quests_spying.Spying, QUEST_TYPE.NORMAL, 1.0, True),
               ('HUNT', 1, 'охота', questgen_quests_hunt.Hunt, QUEST_TYPE.CHARACTER, 1.0, False),
               ('HOMETOWN', 2, 'посетить родной город', questgen_quests_hometown.Hometown, QUEST_TYPE.CHARACTER, 1.0, False),
               ('SEARCH_SMITH', 3, 'посетить кузнеца', questgen_quests_search_smith.SearchSmith, QUEST_TYPE.NORMAL, 0.25, False),
               ('DELIVERY', 4, 'доставка', questgen_quests_delivery.Delivery, QUEST_TYPE.NORMAL, 1.0, True),
               ('CARAVAN', 5, 'караван', questgen_quests_caravan.Caravan, QUEST_TYPE.NORMAL, 1.0, True),
               ('COLLECT_DEBT', 6, 'возвращение долга', questgen_quests_collect_debt.CollectDebt, QUEST_TYPE.NORMAL, 1.0, True),
               ('HELP_FRIEND', 7, 'помощь соратнику', questgen_quests_help_friend.HelpFriend, QUEST_TYPE.CHARACTER, 1.0, False),
               ('INTERFERE_ENEMY', 8, 'вред противнику', questgen_quests_interfere_enemy.InterfereEnemy, QUEST_TYPE.CHARACTER, 1.0, False),
               ('HELP', 9, 'помощь', questgen_quests_help.Help, QUEST_TYPE.NORMAL, 1.0, True),
               ('PILGRIMAGE', 10, 'паломничество', questgen_quests_pilgrimage.Pilgrimage, QUEST_TYPE.UNIQUE, 0.1, False))


class UPGRADE_EQUIPMENT_VARIANTS(rels_django.DjangoEnum):
    records = (('BUY', 0, 'купить'),
               ('SHARP', 1, 'заточить'),
               ('REPAIR', 2, 'починить'))


class PERSON_ACTION(rels_django.DjangoEnum):
    records = (('HELP', 0, 'помочь'),
               ('HARM', 1, 'навредить'))
