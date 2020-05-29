
import smart_imports

smart_imports.all()


class _PreferencesMetaclass(type):

    @classmethod
    def create_preference_getter(cls, preference):

        def getter(self):
            return self._get(preference)
        getter.__name__ = preference.base_name

        return getter

    def __new__(mcs, name, bases, attributes):

        for preference in relations.PREFERENCE_TYPE.records:
            getter = mcs.create_preference_getter(preference)
            attributes[getter.__name__] = property(getter)

        return super(_PreferencesMetaclass, mcs).__new__(mcs, name, bases, attributes)


class HeroPreferences(object, metaclass=_PreferencesMetaclass):
    __slots__ = ('data', 'hero')

    def __init__(self):
        self.data = {}
        self.hero = None

    def serialize(self):
        return self.data

    @classmethod
    def deserialize(cls, data):
        obj = cls()

        obj.data = data

        return obj

    def value_to_set(self, value):
        if isinstance(value, utils_prototypes.BasePrototype):
            return value.id if value is not None else None
        if isinstance(value, mobs_objects.MobRecord):
            return value.id if value is not None else None
        if isinstance(value, places_objects.Place):
            return value.id if value is not None else None
        if isinstance(value, persons_objects.Person):
            return value.id if value is not None else None
        if isinstance(value, rels.Record):
            return value.value if value is not None else None
        return value

    def set(self, preferences_type, value):
        value = self.value_to_set(value)

        if preferences_type.base_name in self.data and value == self.data[preferences_type.base_name]['value']:
            return False

        self.data[preferences_type.base_name] = {'value': value}
        models.HeroPreferences.update(self.hero.id, preferences_type.base_name, value)

        self.hero.reset_accessors_cache()

        return True

    def _prepair_value(self, value):
        return value

    def _prepair_mob(self, mob_id):
        mob = mobs_storage.mobs.get(mob_id)

        if mob and not mob.state.is_ENABLED:
            self.set(relations.PREFERENCE_TYPE.MOB, None)
            return None

        return mob

    def _prepair_place(self, place_id):
        return places_storage.places.get(place_id)

    def _prepair_person(self, person_id):
        return persons_storage.persons.get(person_id)

    def _prepair_energy_regeneration(self, energy_regeneration_id):
        return relations.ENERGY_REGENERATION.index_value.get(int(energy_regeneration_id))

    def _prepair_equipment_slot(self, slot_id):
        if slot_id is None:
            return None
        return relations.EQUIPMENT_SLOT.index_value.get(int(slot_id))

    def _prepair_risk_level(self, risk_id):
        if risk_id is None:
            return None
        return relations.RISK_LEVEL.index_value.get(int(risk_id))

    def _prepair_archetype(self, archetype_id):
        if archetype_id is None:
            return None
        return game_relations.ARCHETYPE.index_value.get(int(archetype_id))

    def _prepair_companion_dedication(self, companion_dedication_id):
        if companion_dedication_id is None:
            return None
        return relations.COMPANION_DEDICATION.index_value.get(int(companion_dedication_id))

    def _prepair_companion_empathy(self, companion_empathy_id):
        if companion_empathy_id is None:
            return None
        return relations.COMPANION_EMPATHY.index_value.get(int(companion_empathy_id))

    def _prepair_quests_region_size(self, value):
        return int(value)

    def _get(self, preferences_type):
        if preferences_type.base_name not in self.data:
            return None

        value = self.data[preferences_type.base_name]['value']

        return getattr(self, preferences_type.prepair_method)(value)

    # helpers

    def place_is_hometown(self, place):
        return self.place is not None and self.place.id == place.id

    def has_person_in_preferences(self, person):
        return ((self.friend is not None and self.friend.id == person.id) or
                (self.enemy is not None and self.enemy.id == person.id))

    @classmethod
    def _preferences_query(cls, all):
        current_time = datetime.datetime.now()

        filter = django_models.Q(hero__premium_state_end_at__gte=current_time)

        if all:
            filter |= django_models.Q(hero__active_state_end_at__gte=current_time)

        return models.HeroPreferences.objects.filter(filter, hero__is_fast=False, hero__ban_state_end_at__lt=current_time)

    @classmethod
    def _heroes_query(cls, all):
        current_time = datetime.datetime.now()

        filter = django_models.Q(premium_state_end_at__gte=current_time)

        if all:
            filter |= django_models.Q(active_state_end_at__gte=current_time)

        return models.Hero.objects.filter(filter, is_fast=False, ban_state_end_at__lt=current_time)

    @classmethod
    def _place_heroes_query(cls, place, all):
        persons_ids = [person.id for person in place.persons]

        db_filter = django_models.Q(place_id=place.id)
        db_filter |= django_models.Q(friend_id__in=persons_ids)
        db_filter |= django_models.Q(enemy_id__in=persons_ids)

        return cls._preferences_query(all=all).filter(db_filter)

    @classmethod
    def get_friends_of(cls, person, all):
        return [logic.load_hero(hero_model=record) for record in cls._heroes_query(all=all).filter(heropreferences__friend_id=person.id)]

    @classmethod
    def get_enemies_of(cls, person, all):
        return [logic.load_hero(hero_model=record) for record in cls._heroes_query(all=all).filter(heropreferences__enemy_id=person.id)]

    @classmethod
    def get_citizens_of(cls, place, all):
        return [logic.load_hero(hero_model=record) for record in cls._heroes_query(all=all).filter(heropreferences__place_id=place.id)]

    @classmethod
    def count_habit_values(cls, place, all):

        honor_positive = 0
        honor_negative = 0
        peacefulness_positive = 0
        peacefulness_negative = 0

        for honor, peacefulness in cls._place_heroes_query(place, all=all).values_list('hero__habit_honor', 'hero__habit_peacefulness'):
            if honor > 0:
                honor_positive += honor
            elif honor < 0:
                honor_negative += honor

            if peacefulness > 0:
                peacefulness_positive += peacefulness
            elif peacefulness < 0:
                peacefulness_negative += peacefulness

        return ((honor_positive, honor_negative),
                (peacefulness_positive, peacefulness_negative))
