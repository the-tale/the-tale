
import smart_imports

smart_imports.all()


class Emissary(game_names.ManageNameMixin2,
               game_attributes.AttributesMixin):
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
                 'attrs',
                 'traits',
                 'abilities',
                 'place_rating_position',

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
                 health,
                 attrs,
                 traits,
                 abilities,
                 place_rating_position):
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
        self.attrs = attrs
        self.traits = traits
        self.abilities = abilities
        self.place_rating_position = place_rating_position

    def is_place_leader(self):
        if self.place_rating_position is None:
            return False

        if self.state.is_OUT_GAME:
            return False

        return self.place_rating_position < tt_emissaries_constants.PLACE_LEADERS_NUMBER

    @property
    def place(self):
        return places_storage.places[self.place_id]

    def active_events(self):
        return storage.events.emissary_events(self.id)

    @property
    def url(self):
        return utils_urls.url('game:emissaries:show', self.id)

    def meta_object(self):
        return meta_relations.Emissary.create_from_object(self)

    def linguistics_restrictions(self):
        return (linguistics_restrictions.get(game_relations.ACTOR.EMISSARY),
                linguistics_restrictions.get(self.gender),
                linguistics_restrictions.get(self.race))

    def _effects_generator(self):
        yield tt_api_effects.Effect(name='телосложение',
                                    attribute=relations.ATTRIBUTE.MAX_HEALTH,
                                    value=tt_emissaries_constants.MAXIMUM_HEALTH)

        for ability in relations.ABILITY.records:
            yield tt_api_effects.Effect(name='способности',
                                        attribute=getattr(relations.ATTRIBUTE, 'ATTRIBUTE_MAXIMUM__{}'.format(ability.name)),
                                        value=tt_emissaries_constants.NORMAL_ATTRIBUTE_MAXIMUM)

            yield tt_api_effects.Effect(name='способности',
                                        attribute=getattr(relations.ATTRIBUTE, 'ATTRIBUTE_GROW_SPEED__{}'.format(ability.name)),
                                        value=tt_emissaries_constants.ATTRIBUT_INCREMENT_DELTA)

        yield tt_api_effects.Effect(name='телосложение',
                                    attribute=relations.ATTRIBUTE.DAMAGE_TO_HEALTH,
                                    value=tt_emissaries_constants.NORMAL_DAMAGE_TO_HEALTH)

        yield tt_api_effects.Effect(name='способности',
                                    attribute=relations.ATTRIBUTE.MAXIMUM_SIMULTANEOUSLY_EVENTS,
                                    value=tt_clans_constants.SIMULTANEOUS_EMISSARY_EVENTS)

        yield tt_api_effects.Effect(name='способности',
                                    attribute=relations.ATTRIBUTE.POSITIVE_POWER,
                                    value=1.0)

        yield tt_api_effects.Effect(name='способности',
                                    attribute=relations.ATTRIBUTE.NEGATIVE_POWER,
                                    value=1.0)

        yield tt_api_effects.Effect(name='способности',
                                    attribute=relations.ATTRIBUTE.CLAN_EXPERIENCE,
                                    value=1.0)

        for trait in self.traits:
            yield tt_api_effects.Effect(name=trait.text,
                                        attribute=trait.attribute,
                                        value=trait.modification)

    def can_participate_in_pvp(self):
        return tt_emissaries_constants.ATTRIBUTES_FOR_PARTICIPATE_IN_PVP <= self.abilities.total_level()

    def protectorat_event_bonus(self):
        region = places_storage.clans_regions.region_for_place(self.place_id)

        if region.clan_id != self.clan_id:
            return 0

        return region.event_bonus()

    def ui_info(self):
        clan_info = clans_storage.infos[self.clan_id]

        return {'id': self.id,
                'name': self.name,
                'race': self.race.value,
                'gender': self.gender.value,
                'place': self.place.id,
                'clan': clan_info.ui_info(),
                'health': self.health,
                'max_health': self.attrs.max_health}

    def __eq__(self, other):
        return all(getattr(self, field, None) == getattr(other, field, None)
                   for field in self.__slots__
                   if field not in ('_utg_name_form__lazy', '_name__lazy'))

    def __ne__(self, other):
        return not self.__eq__(other)


class Event:
    __slots__ = ('id',
                 'emissary_id',
                 'state',
                 'stop_reason',
                 'created_at_turn',
                 'updated_at_turn',
                 'concrete_event',
                 'created_at',
                 'updated_at',
                 'steps_processed',
                 'stop_after_steps')

    def __init__(self,
                 id,
                 emissary_id,
                 state,
                 stop_reason,
                 created_at_turn,
                 updated_at_turn,
                 concrete_event,
                 created_at,
                 updated_at,
                 steps_processed,
                 stop_after_steps):
        self.id = id
        self.emissary_id = emissary_id
        self.state = state
        self.stop_reason = stop_reason
        self.created_at_turn = created_at_turn
        self.updated_at_turn = updated_at_turn
        self.concrete_event = concrete_event
        self.created_at = created_at
        self.updated_at = updated_at
        self.steps_processed = steps_processed
        self.stop_after_steps = stop_after_steps

    @property
    def stop_after(self):
        expected_steps = int(math.floor((datetime.datetime.now() - self.created_at).total_seconds() / (60 * 60)))

        return self.created_at + datetime.timedelta(hours=self.stop_after_steps + expected_steps - self.steps_processed)

    @property
    def emissary(self):
        return storage.emissaries[self.emissary_id]

    def __eq__(self, other):
        return all(getattr(self, field, None) == getattr(other, field, None)
                   for field in self.__slots__)

    def __ne__(self, other):
        return not self.__eq__(other)
