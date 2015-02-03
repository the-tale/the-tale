# coding: utf-8
import time

from dext.common.utils import s11n

from the_tale.common.utils import bbcode

from the_tale.game import names

from the_tale.game.balance import formulas as f
from the_tale.game.balance import constants as c

from the_tale.game.heroes import relations as heroes_relations

from the_tale.game.companions.abilities import container as abilities_container



class Companion(object):
    __slots__ = ('record', 'health', 'coherence', 'experience', 'healed_at', '_hero')

    def __init__(self, record, health, coherence, experience, healed_at, _hero=None):
        self.record = record
        self.health = health
        self.coherence = coherence
        self.experience = experience
        self.healed_at = healed_at
        self._hero = _hero

    def serialize(self):
        return {'record': self.record.id,
                'health': self.health,
                'coherence': self.coherence,
                'experience': self.experience,
                'healed_at': self.healed_at}

    @classmethod
    def deserialize(cls, hero, data):
        from the_tale.game.companions import storage
        obj = cls(record=storage.companions[data['record']],
                  health=data['health'],
                  coherence=data['coherence'],
                  experience=data['experience'],
                  healed_at=data['healed_at'],
                  _hero=hero)
        return obj

    @property
    def name(self): return self.record.name

    @property
    def utg_name_form(self): return self.record.utg_name_form

    def linguistics_restrictions(self):
        from the_tale.linguistics.relations import TEMPLATE_RESTRICTION_GROUP
        from the_tale.linguistics.storage import restrictions_storage

        return [restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_TYPE, self.record.type.value),
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_DEDICATION, self.record.dedication.value),
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_RARITY, self.record.rarity.value),
                restrictions_storage.get_restriction(TEMPLATE_RESTRICTION_GROUP.COMPANION_ARCHETYPE, self.record.archetype.value)]

    @property
    def defend_in_battle_probability(self):
        return self.record.dedication.block_multiplier * self._hero.preferences.companion_dedication.block_multiplier * f.companions_defend_in_battle_probability(self.coherence)

    @property
    def max_health(self): return self.record.max_health

    def hit(self): self.health -= 1

    def on_heal_started(self):
        self.healed_at = time.time()

    @property
    def need_heal_in_settlement(self):
        if self.health == self.max_health:
            return False

        heals_in_hour = f.companions_heal_in_hour(self.health / 2, self.max_health)

        return self.healed_at + 60*60 / heals_in_hour < time.time()


    @property
    def need_heal_in_move(self):
        if self.health == self.max_health:
            return False

        heals_in_hour = f.companions_heal_in_hour(self.health, self.max_health)

        return self.healed_at + 60*60 / heals_in_hour < time.time()


    @property
    def is_dead(self): return self.health <= 0


    def add_experience(self, value):
        self.experience += int(round(self._hero.modify_attribute(heroes_relations.MODIFIERS.COHERENCE_EXPERIENCE, value)))

        if self.coherence == c.COMPANIONS_MAX_COHERENCE:
            self.experience = min(self.experience, self.experience_to_next_level)
            return

        while self.experience_to_next_level <= self.experience:
            self.experience -= self.experience_to_next_level
            self.coherence += 1
            self._hero.reset_accessors_cache()

    def modify_attribute(self, modifier, value):
        return self.record.abilities.modify_attribute(self.coherence, modifier, value)

    def check_attribute(self, modifier):
        return self.record.abilities.check_attribute(self.coherence, modifier)

    def update_context(self, actor, enemy):
        return self.record.abilities.update_context(self.coherence, actor, enemy)

    @property
    def experience_to_next_level(self):
        return f.companions_coherence_for_level(min(self.coherence + 1, c.COMPANIONS_MAX_COHERENCE))


    def ui_info(self):
        return {'id': self.record.id,
                'name': self.name[0].upper() + self.name[1:],
                'health': self.health,
                'max_health': self.max_health,
                'experience': self.experience,
                'experience_to_level': self.coherence_experience_to_next_level,
                'coherence': self.coherence}


class CompanionRecord(names.ManageNameMixin):
    __slots__ = ('id', 'state', 'data', 'type', 'max_health', 'dedication', 'rarity', 'archetype', 'mode', 'abilities')

    def __init__(self,
                 id,
                 state,
                 data,
                 type,
                 max_health,
                 dedication,
                 rarity,
                 archetype,
                 mode):
        self.id = id
        self.state = state
        self.type = type
        self.max_health = max_health
        self.dedication = dedication
        self.rarity = rarity
        self.archetype = archetype
        self.mode = mode

        self.data = data

        self.description = self.data['description']
        self.abilities = abilities_container.Container.deserialize(self.data.get('abilities', {}))

    @classmethod
    def from_model(cls, model):
        return cls(id=model.id,
                   state=model.state,
                   data=s11n.from_json(model.data),
                   type=model.type,
                   max_health=model.max_health,
                   dedication=model.dedication,
                   rarity=model.rarity,
                   archetype=model.archetype,
                   mode=model.mode)

    @property
    def description_html(self): return bbcode.render(self.description)

    def __eq__(self, other):
        return all(getattr(self, field) == getattr(other, field)
                   for field in self.__slots__)
