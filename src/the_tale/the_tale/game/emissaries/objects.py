
import smart_imports

smart_imports.all()


class Emissary(game_names.ManageNameMixin2):
    __slots__ = ('id',
                 'updated_at',
                 'updated_at_turn',
                 'created_at',
                 'created_at_turn',
                 'moved_at',
                 'moved_at_turn',
                 'place_id',
                 'clan_id',
                 'gender',
                 'race',
                 'utg_name',
                 'state',
                 'remove_reason',
                 'health',

                 # mames mixin
                 '_utg_name_form__lazy',
                 '_name__lazy')

    def __init__(self,
                 id,
                 updated_at,
                 updated_at_turn,
                 created_at,
                 created_at_turn,
                 moved_at,
                 moved_at_turn,
                 place_id,
                 clan_id,
                 gender,
                 race,
                 utg_name,
                 state,
                 remove_reason,
                 health):
        self.id = id
        self.updated_at = updated_at
        self.updated_at_turn = updated_at_turn
        self.created_at = created_at
        self.created_at_turn = created_at_turn
        self.moved_at = moved_at
        self.moved_at_turn = moved_at_turn
        self.place_id = place_id
        self.clan_id = clan_id
        self.gender = gender
        self.race = race
        self.utg_name = utg_name
        self.state = state
        self.remove_reason = remove_reason
        self.health = health

    @property
    def place(self):
        return places_storage.places[self.place_id]

    @property
    def url(self):
        return dext_urls.url('game:persons:show', self.id)

    def meta_object(self):
        return meta_relations.Emissary.create_from_object(self)

    def linguistics_restrictions(self):
        return (linguistics_restrictions.get(game_relations.ACTOR.EMISSARY),
                linguistics_restrictions.get(self.gender),
                linguistics_restrictions.get(self.race))

    @property
    def max_health(self):
        return tt_clans_constants.MAXIMUM_EMISSARY_HEALTH

    def ui_info(self):
        return {'id': self.id,
                'name': self.name,
                'race': self.race.value,
                'gender': self.gender.value,
                'place': self.place.id,
                'clan_id': self.clan_id,
                'health': self.health,
                'max_health': self.max_health}

    def __eq__(self, other):
        return all(getattr(self, field, None) == getattr(other, field, None)
                   for field in self.__slots__
                   if field not in ('_utg_name_form__lazy', '_name__lazy'))

    def __ne__(self, other):
        return not self.__eq__(other)
