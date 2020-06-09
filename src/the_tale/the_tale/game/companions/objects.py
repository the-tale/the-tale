
import smart_imports

smart_imports.all()


class Companion(object):
    __slots__ = ('record_id', 'health', 'coherence', 'experience', 'healed_at_turn', '_hero', '_heals_count', '_heals_wounds_count')

    def __init__(self, record_id, health, coherence, experience, healed_at_turn, _hero=None, _heals_count=0, _heals_wounds_count=0):
        self.record_id = record_id
        self.health = health
        self.coherence = coherence
        self.experience = experience
        self.healed_at_turn = healed_at_turn
        self._hero = _hero
        self._heals_count = _heals_count
        self._heals_wounds_count = _heals_wounds_count

    @property
    def record(self):
        return storage.companions[self.record_id]

    def serialize(self):
        return {'record': self.record_id,
                'health': self.health,
                'coherence': self.coherence,
                'experience': self.experience,
                'healed_at_turn': self.healed_at_turn,
                '_heals_count': self._heals_count,
                '_heals_wounds_count': self._heals_wounds_count}

    @classmethod
    def deserialize(cls, data):
        obj = cls(record_id=data['record'],
                  health=int(data['health']),
                  coherence=data['coherence'],
                  experience=data['experience'],
                  healed_at_turn=data.get('healed_at_turn', 0),
                  _heals_count=data.get('_heals_count', 0),
                  _heals_wounds_count=data.get('_heals_wounds_count', 0))
        return obj

    @property
    def name(self): return self.record.name

    @property
    def type(self): return self.record.type

    @property
    def utg_name_form(self): return self.record.utg_name_form

    def linguistics_variables(self):
        return [('weapon', random.choice(self.record.weapons))]

    def linguistics_restrictions(self):
        restrictions = [linguistics_restrictions.get_raw('COMPANION', self.record.id),
                        linguistics_restrictions.get(game_relations.ACTOR.COMPANION),
                        linguistics_restrictions.get(self.record.dedication),
                        linguistics_restrictions.get(self.record.archetype),
                        linguistics_restrictions.get(self.record.communication_verbal),
                        linguistics_restrictions.get(self.record.communication_gestures),
                        linguistics_restrictions.get(self.record.communication_telepathic),
                        linguistics_restrictions.get(self.record.intellect_level),
                        linguistics_restrictions.get(self.record.type),
                        linguistics_restrictions.get(relations.COMPANION_EXISTENCE.HAS_NO),
                        linguistics_restrictions.get(self.record.structure),
                        linguistics_restrictions.get(self.record.movement),
                        linguistics_restrictions.get(self.record.body),
                        linguistics_restrictions.get(self.record.size),
                        linguistics_restrictions.get(self.record.orientation)]

        for feature in self.record.features:
            restrictions.append(linguistics_restrictions.get(feature))

        if self._hero:
            terrain = self._hero.position.cell().terrain

            restrictions.extend((linguistics_restrictions.get(self._hero.actions.current_action.ui_type),
                                 linguistics_restrictions.get(terrain),
                                 linguistics_restrictions.get(terrain.meta_terrain),
                                 linguistics_restrictions.get(terrain.meta_height),
                                 linguistics_restrictions.get(terrain.meta_vegetation)))

        return restrictions

    @property
    def defend_in_battle_probability(self):
        return (self.record.dedication.block_multiplier *
                self._hero.preferences.companion_dedication.block_multiplier *
                f.companions_defend_in_battle_probability(self.actual_coherence) *
                self._hero.companion_block_probability_multiplier)

    @property
    def max_health(self):
        return int(self.record.max_health * self._hero.companion_max_health_multiplier)

    def on_accessors_cache_changed(self):
        self.health = min(self.health, self.max_health)

    def on_settupped(self):
        self.health = self.max_health

    def heal(self, delta):
        if delta < 0:
            raise exceptions.HealCompanionForNegativeValueError(delta=delta)
        old_health = self.health
        self.health = int(min(self.health + delta, self.max_health))

        if old_health == 0:
            self._hero.reset_accessors_cache()

        return self.health - old_health

    @property
    def max_coherence(self):
        return self._hero.companion_max_coherence

    def hit(self):
        old_health = self.health

        self.health -= self._hero.companion_damage

        if random.random() < self._damage_from_heal_probability() / (self._damage_from_heal_probability() + self._hero.companion_damage_probability):
            self._heals_wounds_count += float(c.COMPANIONS_DAMAGE_PER_WOUND) / c.COMPANIONS_HEALTH_PER_HEAL

        if self.health < 0:
            self.health = 0

        return old_health - self.health

    def on_heal_started(self):
        self.healed_at_turn = game_turn.number()
        self._heals_count += 1

    def _damage_from_heal_probability(self):
        return (c.COMPANIONS_WOUNDS_IN_HOUR_FROM_HEAL / (c.BATTLES_PER_HOUR * (c.BATTLE_LENGTH / 2) * self.defend_in_battle_probability))

    @property
    def damage_from_heal_probability(self):

        if self._hero.companion_heal_disabled():
            return self._damage_from_heal_probability()

        if self._heals_count < self._heals_wounds_count:
            return 0

        return self._damage_from_heal_probability() * 2

    @property
    def need_heal(self):
        if self.health == self.max_health:
            return False

        return self.healed_at_turn + c.TURNS_IN_HOUR / c.COMPANIONS_HEALS_IN_HOUR <= game_turn.number()

    @property
    def is_dead(self):
        return self.health <= 0

    def add_experience(self, value, force=False):

        if not force:
            value = value * self._hero.companion_coherence_experience * self._hero.companion_coherence_speed

        self.experience += int(value)

        while self.experience_to_next_level <= self.experience:

            if self.coherence >= self.max_coherence:
                if self.coherence >= c.COMPANIONS_MAX_COHERENCE:
                    # полностью заплняем шкалу опыта, когда он на максимуме
                    self.experience = self.experience_to_next_level
                    break

                elif not force:
                    self.experience = min(self.experience, self.experience_to_next_level - 1)
                    break

                else:
                    pass

            self.experience -= self.experience_to_next_level
            self.coherence += 1

            self._hero.reset_accessors_cache()

    def has_full_experience(self):
        return (self.coherence == c.COMPANIONS_MAX_COHERENCE and
                self.experience_to_next_level == self.experience)

    @property
    def actual_coherence(self):
        return min(self.max_coherence, self.coherence)

    def modification_coherence(self, modifier):
        if modifier.is_COMPANION_MAX_COHERENCE:
            return self.coherence
        else:
            return self.actual_coherence

    def modify_attribute(self, modifier, value):
        if modifier.is_COMPANION_ABILITIES_LEVELS:
            return value

        return self.record.abilities.modify_attribute(self.modification_coherence(modifier),
                                                      self._hero.companion_abilities_levels,
                                                      modifier,
                                                      value,
                                                      is_dead=self.is_dead)

    def check_attribute(self, modifier):
        return self.record.abilities.check_attribute(self.modification_coherence(modifier),
                                                     modifier,
                                                     is_dead=self.is_dead)

    @property
    def experience_to_next_level(self):
        return f.companions_coherence_for_level(min(self.coherence + 1, c.COMPANIONS_MAX_COHERENCE))

    @property
    def basic_damage(self):
        distribution = self.record.archetype.power_distribution
        raw_damage = f.expected_damage_to_mob_per_hit(self._hero.level)
        return power.Damage(physic=raw_damage * distribution.physic, magic=raw_damage * distribution.magic)

    def ui_info(self):
        return {'type': self.record.id,
                'name': self.name[0].upper() + self.name[1:],
                'health': self.health,
                'max_health': self.max_health,
                'experience': self.experience,
                'experience_to_level': self.experience_to_next_level,
                'coherence': self.actual_coherence,
                'real_coherence': self.coherence}


class CompanionRecord(game_names.ManageNameMixin2):
    __slots__ = ('id',
                 'state',
                 'type',
                 'max_health',
                 'dedication',
                 'archetype',
                 'mode',
                 'abilities',
                 'communication_verbal',
                 'communication_gestures',
                 'communication_telepathic',
                 'intellect_level',

                 'structure',
                 'features',
                 'movement',
                 'body',
                 'size',
                 'orientation',
                 'weapons',

                 'description',
                 'utg_name',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self,
                 id,
                 state,
                 type,
                 max_health,
                 dedication,
                 archetype,
                 mode,
                 communication_verbal,
                 communication_gestures,
                 communication_telepathic,
                 intellect_level,

                 structure,
                 features,
                 movement,
                 body,
                 size,
                 orientation,
                 weapons,

                 abilities,

                 description,
                 utg_name):
        self.id = id
        self.state = state
        self.type = type
        self.max_health = max_health
        self.dedication = dedication
        self.archetype = archetype
        self.mode = mode

        self.communication_verbal = communication_verbal
        self.communication_gestures = communication_gestures
        self.communication_telepathic = communication_telepathic
        self.intellect_level = intellect_level

        self.structure = structure
        self.features = features
        self.movement = movement
        self.body = body
        self.size = size
        self.orientation = orientation
        self.weapons = weapons

        self.utg_name = utg_name

        self.description = description
        self.abilities = abilities

        if not self.weapons:
            raise exceptions.NoWeaponsError(companion_id=self.id)

    def features_verbose(self):
        features = [feature.verbose_text for feature in self.features]
        features.sort()
        return ', '.join(features)

    def weapons_verbose(self):
        weapons = []

        for weapon in self.weapons:
            weapons.append(weapon.verbose())

        weapons.sort()

        return weapons

    def rarity_points(self):
        points = [('здоровье', float(self.max_health - c.COMPANIONS_MEDIUM_HEALTH) / (c.COMPANIONS_MEDIUM_HEALTH - c.COMPANIONS_MIN_HEALTH) * 1)]

        # dedication does not affect rarity ?

        for coherence, ability in self.abilities.all_abilities:
            points.append((ability.text, ability.rarity_delta))

        return points

    @property
    def raw_rarity(self):
        return sum((points for text, points in self.rarity_points()), 0)

    @property
    def rarity(self):
        return relations.RARITY(max(0, min(4, int(round(self.raw_rarity - 0.0001)) - 1)))

    @classmethod
    def from_model(cls, model):
        data = s11n.from_json(model.data)

        weapons = [artifacts_objects.Weapon.deserialize(weapon_data)
                   for weapon_data in data.get('weapons', ())]

        return cls(id=model.id,
                   state=model.state,
                   type=model.type,
                   max_health=model.max_health,
                   dedication=model.dedication,
                   archetype=model.archetype,
                   mode=model.mode,
                   communication_verbal=model.communication_verbal,
                   communication_gestures=model.communication_gestures,
                   communication_telepathic=model.communication_telepathic,
                   intellect_level=model.intellect_level,

                   abilities=companions_abilities_container.Container.deserialize(data.get('abilities', {})),

                   utg_name=utg_words.Word.deserialize(data['name']),
                   description=data['description'],

                   structure=tt_beings_relations.STRUCTURE(data.get('structure', 0)),
                   features=frozenset(tt_beings_relations.FEATURE(feature) for feature in data.get('features', ())),
                   movement=tt_beings_relations.MOVEMENT(data.get('movement', 0)),
                   body=tt_beings_relations.BODY(data.get('body', 0)),
                   size=tt_beings_relations.SIZE(data.get('size', 0)),
                   orientation=tt_beings_relations.ORIENTATION(data.get('orientation', 0)),
                   weapons=weapons)

    @property
    def description_html(self): return bbcode_renderers.default.render(self.description)

    def __eq__(self, other):
        return all(getattr(self, field, None) == getattr(other, field, None)
                   for field in self.__slots__
                   if field not in ('_utg_name_form__lazy', '_name__lazy'))

    def meta_object(self):
        return meta_relations.Companion.create_from_object(self)
