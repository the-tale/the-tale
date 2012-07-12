# coding: utf-8

from game.balance import calculated as calc

from game.mobs.storage import MobsDatabase

from game.map.places.models import Place
from game.map.places.prototypes import PlacePrototype

from game.heroes.models import ChoosePreferencesTask, PREFERENCE_TYPE, CHOOSE_PREFERENCES_STATE


class HeroPreferences(object):

    def __init__(self, hero_model):
        self.hero_model = hero_model

    def get_mob_id(self): return self.hero_model.pref_mob_id
    def set_mob_id(self, value): self.hero_model.pref_mob_id = value
    mob_id = property(get_mob_id, set_mob_id)

    @property
    def mob(self):
        if self.mob_id is None:
            return None
        return MobsDatabase.storage()[self.mob_id]


    def get_place_id(self): return self.hero_model.pref_place_id
    def set_place_id(self, value): self.hero_model.pref_place_id = value
    place_id = property(get_place_id, set_place_id)

    @property
    def place(self):
        if not hasattr(self, '_place'):
            self._place = PlacePrototype(model=self.hero_model.pref_place) if self.hero_model.pref_place else None
        return self._place



class ChoosePreferencesTaskPrototype(object):

    def __init__(self, model):
        self.model = model

    @classmethod
    def get_by_id(cls, id_):
        try:
            return cls(ChoosePreferencesTask.objects.get(id=id_))
        except ChoosePreferencesTask.DoesNotExist:
            return None

    @classmethod
    def create(cls, hero, preference_type, preference_id):

        model = ChoosePreferencesTask.objects.create(hero=hero.model,
                                                     preference_type=preference_type,
                                                     preference_id=str(preference_id))

        return cls(model)

    @classmethod
    def reset_all(cls):
        ChoosePreferencesTask.objects.filter(state=CHOOSE_PREFERENCES_STATE.WAITING).update(state=CHOOSE_PREFERENCES_STATE.RESET)

    @property
    def state(self): return self.model.state

    @property
    def id(self): return self.model.id

    @property
    def hero_id(self): return self.model.hero_id

    @property
    def is_unprocessed(self):
        return self.model.state == CHOOSE_PREFERENCES_STATE.WAITING

    def process(self, bundle):

        if not self.is_unprocessed:
            return

        hero = bundle.heroes[self.model.hero_id]

        if self.model.preference_type == PREFERENCE_TYPE.MOB:

            if hero.level < calc.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED:
                self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, calc.CHARACTER_PREFERENCES_MOB_LEVEL_REQUIRED)
                self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                return

            if self.model.preference_id not in MobsDatabase.storage():
                self.model.comment = u'unknown mob id: %s' % (self.model.preference_id, )
                self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                return

            mob = MobsDatabase.storage()[self.model.preference_id]

            if hero.level < mob.level:
                self.model.comment = u'hero level < mob level (%d < %d)' % (hero.level, mob.level)
                self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                return

            hero.preferences.mob_id = mob.id

        elif self.model.preference_type == PREFERENCE_TYPE.PLACE:
            place_id = int(self.model.preference_id)

            if hero.level < calc.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED:
                self.model.comment = u'hero level < required level (%d < %d)' % (hero.level, calc.CHARACTER_PREFERENCES_PLACE_LEVEL_REQUIRED)
                self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                return

            if not Place.objects.filter(id=self.model.preference_id).exists():
                self.model.comment = u'unknown place id: %s' % (place_id, )
                self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
                return

            hero.preferences.place_id = place_id

        else:
            self.model.comment = u'unknown preference type: %s' % (self.model.preference_type, )
            self.model.state = CHOOSE_PREFERENCES_STATE.ERROR
            return


        self.model.state = CHOOSE_PREFERENCES_STATE.PROCESSED


    def save(self):
        self.model.save()
