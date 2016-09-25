# coding: utf-8

from the_tale.game.companions.abilities import exceptions

from the_tale.common.utils.decorators import lazy_property

from the_tale.game.balance import constants as c

from the_tale.game.companions.abilities import effects


class Container(object):

    __slots__ = ('common', 'start', 'coherence', 'honor', 'peacefulness',
                 '_start_abilities__lazy', '_coherence_abilities__lazy', '_all_abilities__lazy')

    def __init__(self, common=(), start=frozenset(), coherence=None, honor=None, peacefulness=None):

        if not isinstance(common, (tuple, list)):
            raise exceptions.NotOrderedUIDSError()

        self.common = tuple(ability for ability in common if ability)
        self.start = frozenset(ability for ability in start if ability)
        self.coherence = coherence
        self.honor = honor
        self.peacefulness = peacefulness

    @lazy_property
    def start_abilities(self):
        abilities = []

        if self.coherence is not None:
            abilities.append(self.coherence)

        if self.honor is not None:
            abilities.append(self.honor)

        if self.peacefulness is not None:
            abilities.append(self.peacefulness)

        for start in self.start:
            abilities.append(start)

        return abilities

    @lazy_property
    def coherence_abilities(self):
        abilities = []

        open_interval = c.COMPANIONS_MAX_COHERENCE / (len(self.common) + 1)

        for i, ability in enumerate(self.common):
            abilities.append((open_interval * (i+1), ability))

        return abilities

    @lazy_property
    def all_abilities(self):
        abilities = [(0, start_ability) for start_ability in self.start_abilities]
        abilities.extend(self.coherence_abilities)
        return abilities

    def has_duplicates(self):
        return len(self.all_abilities) > len(set(ability for coherence, ability in self.all_abilities))

    def has_same_effects(self):
        return len(self.all_abilities) > len(set(ability.effect.uid for coherence, ability in self.all_abilities))

    def has(self, ability):
        return ability in (ability for coherence, ability in self.all_abilities)

    def abilities_for_coherence(self, coherence):
        for barrier_coherence, ability in self.all_abilities:
            if barrier_coherence > coherence:
                break
            yield ability

    def modify_attribute(self, coherence, abilities_levels, modifier, value):
        for ability in self.abilities_for_coherence(coherence):
            value = ability.effect.modify_attribute(abilities_levels, modifier, value)
        return value


    def check_attribute(self, coherence, modifier):
        for ability in self.abilities_for_coherence(coherence):
            if ability.effect.check_attribute(modifier):
                return True

        return False


    def serialize(self):
        return {'common': [ability.value for ability in self.common],
                'start': [ability.value for ability in self.start],
                'coherence': self.coherence.value if self.coherence else None,
                'honor': self.honor.value if self.honor else None,
                'peacefulness': self.peacefulness.value if self.peacefulness else None}


    @classmethod
    def deserialize(cls, data):
        coherence_uid = data.get('coherence')
        honor_uid = data.get('honor')
        peacefulness_uid = data.get('peacefulness')

        return cls(common=tuple(effects.ABILITIES(ability_uid) for ability_uid in data.get('common', ())),
                   start=frozenset(effects.ABILITIES(ability_uid) for ability_uid in data.get('start', frozenset())),
                   coherence=effects.ABILITIES(coherence_uid) if coherence_uid is not None else None,
                   honor=effects.ABILITIES(honor_uid) if honor_uid is not None else None,
                   peacefulness=effects.ABILITIES(peacefulness_uid) if peacefulness_uid is not None else None)


    def __eq__(self, other):
        return  (self.__class__ is other.__class__ and
                 self.common == other.common and
                 self.start == other.start and
                 self.coherence == other.coherence and
                 self.honor == other.honor and
                 self.peacefulness == other.peacefulness)
