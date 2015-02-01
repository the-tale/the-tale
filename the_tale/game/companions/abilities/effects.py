# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from the_tale.game import relations as game_relations

from the_tale.game.balance import constants as c

from the_tale.game.companions.abilities import relations


class Base(object):
    TYPE = None

    def __init__(self):
        pass

    @property
    def uid(self):
        return (self.TYPE, None)

    def modify_attribute(self, coherence, modifier, value):
        return self._modify_attribute(coherence, modifier, value)

    def check_attribute(self, coherence, modifier):
        return self._check_attribute(coherence, modifier)

    def update_context(self, coherence, actor, enemy):
        return self._update_context(coherence, actor, enemy)


    def _modify_attribute(self, coherence, modifier, value):
        return value

    def _check_attribute(self, coherence, modifier):
        return False

    def _update_context(self, coherence, actor, enemy):
        pass



class CoherenceSpeed(Base):
    TYPE = relations.EFFECT.COHERENCE_SPEED

    def __init__(self, speed, **kwargs):
        super(CoherenceSpeed, self).__init__(**kwargs)
        self.speed = speed


class ChangeHabits(Base):
    TYPE = relations.EFFECT.CHANGE_HABITS

    def __init__(self, habit_type, habit_pole, **kwargs):
        super(ChangeHabits, self).__init__(**kwargs)
        self.habit_type = habit_type
        self.habit_pole = habit_pole

    @property
    def uid(self):
        return (self.TYPE, self.habit_type)



def ability_record(uid, name, description, effect):
    return (u'ABILITY_%d' % uid,
            uid,
            name,
            description,
            effect)


class ABILITIES(DjangoEnum):
    description = Column()
    effect = Column(single_type=False)

    records = (
        ability_record(uid=0, name=u'строптивый', description=u'очень медленный рост слаженности', effect=CoherenceSpeed(speed=0.70)),
        ability_record(uid=1, name=u'упрямый', description=u'медленный рост слаженности', effect=CoherenceSpeed(speed=0.85)),
        ability_record(uid=2, name=u'добросовестный', description=u'быстрый рост слаженности', effect=CoherenceSpeed(speed=1.15)),
        ability_record(uid=3, name=u'исполнительный', description=u'очень быстрый рост слаженности', effect=CoherenceSpeed(speed=1.30)),

        ability_record(uid=4, name=u'агрессивный', description=u'повышает агрессивность героя',
                       effect=ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_pole=-c.HABITS_BORDER)),
        ability_record(uid=5, name=u'миролюбивый', description=u'понижает агрессивность героя',
                       effect=ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_pole=c.HABITS_BORDER)),
        ability_record(uid=6, name=u'сдержанный', description=u'склоняет героя к сдержанности',
                       effect=ChangeHabits(habit_type=game_relations.HABIT_TYPE.PEACEFULNESS, habit_pole=0)),

        ability_record(uid=7, name=u'себе на уме', description=u'склоняет героя быть себе на уме',
                       effect=ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_pole=0)),
        ability_record(uid=8, name=u'честный', description=u'повышает честь героя',
                       effect=ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_pole=c.HABITS_BORDER)),
        ability_record(uid=9, name=u'подлый', description=u'понижает честь героя',
                       effect=ChangeHabits(habit_type=game_relations.HABIT_TYPE.HONOR, habit_pole=-c.HABITS_BORDER))
            )
