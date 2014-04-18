# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from questgen.quests.spying import Spying
from questgen.quests.hunt import Hunt
from questgen.quests.hometown import Hometown
from questgen.quests.search_smith import SearchSmith
from questgen.quests.delivery import Delivery
from questgen.quests.caravan import Caravan
from questgen.quests.collect_debt import CollectDebt
from questgen.quests.help_friend import HelpFriend
from questgen.quests.interfere_enemy import InterfereEnemy
from questgen.quests.help import Help
from questgen.quests.pilgrimage import Pilgrimage



class ACTOR_TYPE(DjangoEnum):
    records = (('PERSON', 0, u'житель'),
                ('PLACE', 1, u'место'),
                ('MONEY_SPENDING', 2, u'трата денег'))


class DONOTHING_TYPE(DjangoEnum):
    duration = Column(unique=False)
    messages_probability = Column(unique=False)

    records = (('DRUNK_SONG', 'drunk_song', u'пьяная песня', 6, 0.3),
                ('STAGGER_STREETS', 'stagger_streets', u'шляться по улицам', 10, 0.3),
                ('CHATTING', 'chatting', u'общение с друзьями',  5, 0.3),
                ('SEARCH_OLD_FRIENDS', 'search_old_friends', u'поиск старых друзей', 7, 0.3),
                ('REMEMBER_NAMES', 'remember_names', u'вспоминание имён', 3, 0.3),
                ('SPEAK_WITH_GURU', 'speak_with_guru', u'общение с гуру', 5, 0.1),
                ('STAGGER_HOLY_STREETS', 'stagger_holy_streets', u'бродить по святым улицам', 5, 0.1) )



class QUEST_TYPE(DjangoEnum):
    records = ( ('NORMAL', 0, u'обычный'),
                ('CHARACTER', 1, u'характерный'),
                ('UNIQUE', 2, u'уникальный') )


class QUESTS(DjangoEnum):
    quest_class = Column()
    quest_type = Column(unique=False)
    priority = Column(unique=False)

    records = ( ('SPYING', 0, u'шпионаж', Spying, QUEST_TYPE.NORMAL, 1.0),
                ('HUNT', 1, u'охота', Hunt, QUEST_TYPE.CHARACTER, 1.0),
                ('HOMETOWN', 2, u'посетить родной город', Hometown, QUEST_TYPE.CHARACTER, 1.0),
                ('SEARCH_SMITH', 3, u'посетить кузнеца', SearchSmith, QUEST_TYPE.NORMAL, 0.25),
                ('DELIVERY', 4, u'доставка', Delivery, QUEST_TYPE.NORMAL, 1.0),
                ('CARAVAN', 5, u'караван', Caravan, QUEST_TYPE.NORMAL, 1.0),
                ('COLLECT_DEBT', 6, u'возвращение долга', CollectDebt, QUEST_TYPE.NORMAL, 1.0),
                ('HELP_FRIEND', 7, u'помощь соратнику', HelpFriend, QUEST_TYPE.CHARACTER, 1.0),
                ('INTERFERE_ENEMY', 8, u'вред противнику', InterfereEnemy, QUEST_TYPE.CHARACTER, 1.0),
                ('HELP', 9, u'помощь', Help, QUEST_TYPE.NORMAL, 1.0),
                ('PILGRIMAGE', 10, u'паломничество', Pilgrimage, QUEST_TYPE.UNIQUE, 0.1) )


class UPGRADE_EQUIPMENT_VARIANTS(DjangoEnum):
    records = (('BUY', 0, u'купить'),
               ('SHARP', 1, u'заточить'),
               ('REPAIR', 2, u'починить'))
