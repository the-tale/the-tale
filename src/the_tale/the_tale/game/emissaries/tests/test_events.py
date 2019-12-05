import smart_imports

smart_imports.all()


class BaseEventsMixin(clans_helpers.ClansTestsMixin,
                      helpers.EmissariesTestsMixin):

    Event = None
    EXPECTED_CYCLE_TIME = 1
    EXPECTED_PERIOD_CHOICES_NUMBER = tt_clans_constants.MAX_EVENT_LENGTH

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        clans_tt_services.currencies.cmd_debug_clear_service()
        game_tt_services.debug_clear_service()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

        self.hero = heroes_logic.load_hero(account_id=self.account.id)

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=self.places[0].id)

        politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=666,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                            target_id=self.emissary.id,
                                                                            amount=1000000)])

    def get_event(self):
        if not hasattr(self, 'event'):
            self.event = logic.create_event(initiator=self.account,
                                            emissary=self.emissary,
                                            concrete_event=self.concrete_event,
                                            days=7)
        return self.event

    def get_experience(self):
        return clans_tt_services.currencies.cmd_balance(self.clan.id, currency=clans_relations.CURRENCY.EXPERIENCE)

    def get_event_points(self):
        return tt_services.events_currencies.cmd_balance(self.concrete_event.resource_id(self.emissary),
                                                         currency=self.EVENT_CURRENCY)

    def test_start_dialog(self):
        dialog_url = utils_urls.url('game:emissaries:start-event-dialog',
                                    self.emissary.id,
                                    event_type=self.concrete_event.TYPE.value)
        self.check_html_ok(self.request_ajax_html(dialog_url), texts=[])

    def test_start_event(self, expected_error=None):
        if self.Event.TYPE.availability.is_FOR_LEADERS:
            self.emissary.place_rating_position = 0
            logic.save_emissary(self.emissary)

        start_url = utils_urls.url('game:emissaries:start-event',
                                   self.emissary.id,
                                   event_type=self.concrete_event.TYPE.value)
        self.request_login(self.account.email)

        data = {'period': self.concrete_event.cycle_time(self.emissary)}

        data.update(self._start_event_data())

        if expected_error:
            with self.check_not_changed(models.Event.objects.count):
                self.check_ajax_error(self.post_ajax_json(start_url, data), expected_error)
        else:
            with self.check_delta(models.Event.objects.count, 1):
                self.check_ajax_ok(self.post_ajax_json(start_url, data))

    def _start_event_data(self):
        return {}

    def test_serialization(self):
        self.emissary.place_rating_position = 0
        self.assertTrue(self.emissary.is_place_leader())

        with self.concrete_event.on_create(self.emissary):
            event = self.get_event()

        self.concrete_event.after_create(event)

        self.assertEqual(self.concrete_event,
                         self.Event.deserialize(self.concrete_event.serialize()))

        self.assertEqual(self.concrete_event.serialize(),
                         self.Event.deserialize(self.concrete_event.serialize()).serialize())

    def test_effect_description(self):
        self.concrete_event.effect_description(self.emissary, 1000)

    def test_event_description(self):
        self.concrete_event.event_description(self.emissary)

    def test_cycle_time(self):
        self.assertEqual(self.concrete_event.cycle_time(self.emissary), self.EXPECTED_CYCLE_TIME)

    def test_period_choices(self):
        self.assertEqual(len(self.concrete_event.period_choices(self.emissary)), self.EXPECTED_PERIOD_CHOICES_NUMBER)

    def test_is_available__active_events(self):
        self.emissary.place_rating_position = 0

        self.assertTrue(self.concrete_event.is_available(self.emissary, active_events=()))
        self.assertTrue(self.concrete_event.is_available(self.emissary,
                                                         active_events=(relations.EVENT_TYPE.random(exclude=(self.concrete_event.TYPE,)),)))
        self.assertFalse(self.concrete_event.is_available(self.emissary, active_events=(self.concrete_event.TYPE,)))


# tests for Rest event and its base class
# other tests will be only for concrete event
class RestTests(BaseEventsMixin, utils_testcase.TestCase):

    Event = events.Rest

    def setUp(self):
        super().setUp()

        self.concrete_event = self.Event(raw_ability_power=666)

    def test_event_description(self):
        self.assertEqual(self.concrete_event.effect_description(self.emissary, self.concrete_event.raw_ability_power),
                         self.concrete_event.event_description(self.emissary))

    def test_health_per_step(self):
        self.assertEqual(self.concrete_event.health_per_step(0), 11)
        self.assertEqual(self.concrete_event.health_per_step(250), 13)
        self.assertEqual(self.concrete_event.health_per_step(500), 14)
        self.assertEqual(self.concrete_event.health_per_step(1000), 16)
        self.assertEqual(self.concrete_event.health_per_step(2000), 20)

    def test_ability_power(self):
        self.assertEqual(self.concrete_event.ability_power(777), 777 / tt_emissaries_constants.MAXIMUM_ATTRIBUTE_MAXIMUM)

    def test_get_raw_ability_power(self):
        self.assertCountEqual(self.concrete_event.TYPE.abilities,
                              [relations.ABILITY.TECHNOLOGIES, relations.ABILITY.COVERT_OPERATIONS])

        self.assertEqual(self.emissary.abilities[relations.ABILITY.TECHNOLOGIES], 0)
        self.assertEqual(self.emissary.abilities[relations.ABILITY.COVERT_OPERATIONS], 0)

        self.assertEqual(self.concrete_event.get_raw_ability_power(self.emissary),
                         0)

        self.emissary.abilities[relations.ABILITY.TECHNOLOGIES] = 200
        self.emissary.abilities[relations.ABILITY.COVERT_OPERATIONS] = 600

        self.assertEqual(self.concrete_event.get_raw_ability_power(self.emissary),
                         400)

    def test_action_points_cost_modificator(self):
        self.assertCountEqual(self.concrete_event.TYPE.abilities,
                              [relations.ABILITY.TECHNOLOGIES, relations.ABILITY.COVERT_OPERATIONS])

        self.emissary.traits = frozenset()

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event._action_points_cost_modificator(self.emissary),
                         0)

        self.emissary.traits = frozenset({relations.TRAIT.EVENT_ACTION_POINTS_DELTA__TECHNOLOGIES__POSITIVE,
                                          relations.TRAIT.EVENT_ACTION_POINTS_DELTA__COVERT_OPERATIONS__POSITIVE,
                                          relations.TRAIT.EVENT_ACTION_POINTS_DELTA__SOCIOLOGY__POSITIVE})

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event._action_points_cost_modificator(self.emissary),
                         -2 * tt_clans_constants.PRICE_START_EVENT_DELTA)

        self.emissary.traits = frozenset({relations.TRAIT.EVENT_ACTION_POINTS_DELTA__TECHNOLOGIES__NEGATIVE,
                                          relations.TRAIT.EVENT_ACTION_POINTS_DELTA__COVERT_OPERATIONS__NEGATIVE,
                                          relations.TRAIT.EVENT_ACTION_POINTS_DELTA__SOCIOLOGY__NEGATIVE})

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event._action_points_cost_modificator(self.emissary),
                         2 * tt_clans_constants.PRICE_START_EVENT_DELTA)

    def test_action_points_cost(self):
        self.assertCountEqual(self.concrete_event.TYPE.abilities,
                              [relations.ABILITY.TECHNOLOGIES, relations.ABILITY.COVERT_OPERATIONS])

        self.emissary.traits = frozenset({relations.TRAIT.EVENT_ACTION_POINTS_DELTA__TECHNOLOGIES__POSITIVE,
                                          relations.TRAIT.EVENT_ACTION_POINTS_DELTA__COVERT_OPERATIONS__POSITIVE,
                                          relations.TRAIT.EVENT_ACTION_POINTS_DELTA__SOCIOLOGY__POSITIVE})

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event.action_points_cost(self.emissary),
                         tt_clans_constants.PRICE_START_EVENT *
                         (self.concrete_event.TYPE.action_points_cost_modifier - 2 * tt_clans_constants.PRICE_START_EVENT_DELTA))

    def test_power_for_day_cost(self):
        self.emissary.traits = frozenset()
        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event.power_for_day_cost(self.emissary), 50)

    def test_power_cost_modificator(self):
        self.assertCountEqual(self.concrete_event.TYPE.abilities,
                              [relations.ABILITY.TECHNOLOGIES, relations.ABILITY.COVERT_OPERATIONS])

        self.emissary.traits = frozenset()

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event._power_cost_modificator(self.emissary),
                         0.0)

        self.emissary.traits = frozenset({relations.TRAIT.EVENT_POWER_DELTA__TECHNOLOGIES__POSITIVE,
                                          relations.TRAIT.EVENT_POWER_DELTA__COVERT_OPERATIONS__POSITIVE,
                                          relations.TRAIT.EVENT_POWER_DELTA__SOCIOLOGY__POSITIVE})

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event._power_cost_modificator(self.emissary),
                         -2 * tt_clans_constants.PRICE_START_EVENT_DELTA)

        self.emissary.traits = frozenset({relations.TRAIT.EVENT_POWER_DELTA__TECHNOLOGIES__NEGATIVE,
                                          relations.TRAIT.EVENT_POWER_DELTA__COVERT_OPERATIONS__NEGATIVE,
                                          relations.TRAIT.EVENT_POWER_DELTA__SOCIOLOGY__NEGATIVE})

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event._power_cost_modificator(self.emissary),
                         2 * tt_clans_constants.PRICE_START_EVENT_DELTA)

    def test_power_cost(self):
        self.emissary.traits = frozenset({relations.TRAIT.EVENT_POWER_DELTA__TECHNOLOGIES__POSITIVE,
                                          relations.TRAIT.EVENT_POWER_DELTA__COVERT_OPERATIONS__POSITIVE,
                                          relations.TRAIT.EVENT_POWER_DELTA__SOCIOLOGY__POSITIVE})

        self.emissary.refresh_attributes()

        self.assertEqual(self.concrete_event.power_cost(self.emissary, days=7),
                         int(math.ceil(7 * 50 * (1 - 2 * tt_clans_constants.PRICE_START_EVENT_DELTA))))

    def test_on_step(self):
        self.emissary.health = 1

        logic.save_emissary(self.emissary)

        delta = self.concrete_event.health_per_step(self.concrete_event.raw_ability_power)

        with self.check_delta(lambda: logic.load_emissary(self.emissary.id).health, delta):
            self.concrete_event.on_step(self.get_event())


class DismissTests(BaseEventsMixin, utils_testcase.TestCase):

    Event = events.Dismiss
    EXPECTED_PERIOD_CHOICES_NUMBER = 1

    def setUp(self):
        super().setUp()

        self.concrete_event = self.Event(raw_ability_power=666)

    def test_on_finish(self):
        self.assertTrue(self.emissary.state.is_IN_GAME)

        self.concrete_event.on_finish(self.get_event())

        self.assertTrue(self.emissary.state.is_OUT_GAME)


class RelocationTests(BaseEventsMixin, utils_testcase.TestCase):

    Event = events.Relocation
    EXPECTED_CYCLE_TIME = 2
    EXPECTED_PERIOD_CHOICES_NUMBER = 1

    def setUp(self):
        super().setUp()

        self.concrete_event = self.Event(raw_ability_power=666,
                                         place_id=self.places[1].id)

    def _start_event_data(self):
        return {'place': self.places[1].id}

    def test_on_finish(self):
        self.concrete_event.on_finish(self.get_event())

        self.assertEqual(self.emissary.place_id, self.places[1].id)
        self.assertEqual(logic.load_emissary(self.emissary.id).place_id, self.places[1].id)


class RenameTests(BaseEventsMixin, utils_testcase.TestCase):

    Event = events.Rename
    EXPECTED_PERIOD_CHOICES_NUMBER = 1

    def setUp(self):
        super().setUp()

        self.new_name = game_names.generator().get_test_name()

        self.concrete_event = self.Event(raw_ability_power=666,
                                         new_name=self.new_name)

    def _start_event_data(self):
        return linguistics_helpers.get_word_post_data(self.new_name, prefix='name')

    def test_on_finish(self):
        self.concrete_event.on_finish(self.get_event())

        self.assertEqual(self.emissary.utg_name, self.new_name)
        self.assertEqual(logic.load_emissary(emissary_id=self.emissary.id).utg_name, self.new_name)


class ClanLevelUpMixin(BaseEventsMixin):

    Event = events.PointsGainLevelUp

    def setUp(self):
        super().setUp()

        self.new_name = game_names.generator().get_test_name()

        self.concrete_event = self.Event(raw_ability_power=666)

        self._set_attribute(0)

    def add_experience(self):
        clans_tt_services.currencies.cmd_change_balance(account_id=self.clan.id,
                                                        type='test',
                                                        amount=1005000000,
                                                        asynchronous=False,
                                                        autocommit=True,
                                                        currency=clans_relations.CURRENCY.EXPERIENCE)

    def test_start_event(self):
        self.add_experience()

        with self.check_decreased(self.get_experience):
            super().test_start_event()

    def test_start_event__no_experience(self):
        with self.check_not_changed(self.get_experience):
            super().test_start_event(expected_error='emissaries.event_not_available')

    def test_serialization(self):
        self.add_experience()
        super().test_serialization()

    def _start_event_data(self):
        return linguistics_helpers.get_word_post_data(self.new_name, prefix='name')

    def _set_attribute(self, value):
        clans_tt_services.properties.cmd_set_property(self.clan.id,
                                                      self.Event.PROPERTY.property,
                                                      value)

    def test_is_available__attribute_at_maximum(self):
        self.add_experience()

        self.assertTrue(self.concrete_event.is_available(self.emissary, active_events=()))

        self._set_attribute(self.Event.PROPERTY.maximum)

        self.assertFalse(self.concrete_event.is_available(self.emissary, active_events=()))

    def test_effect_description__attribute_at_maximum(self):
        self._set_attribute(self.Event.PROPERTY.maximum)
        self.assertTrue(self.Event.effect_description(self.emissary, raw_ability_power=666))

    def test_event_description__attribute_at_maximum(self):
        self._set_attribute(self.Event.PROPERTY.maximum)
        self.assertTrue(self.concrete_event.event_description(self.emissary))

    def test_is_available__active_events(self):
        self.add_experience()
        super().test_is_available__active_events()

    def test_on_create__initialization(self):
        self.add_experience()

        self._set_attribute(6)

        with self.concrete_event.on_create(self.emissary):
            pass

        self.assertNotEqual(self.concrete_event.transaction_id, None)
        self.assertEqual(self.concrete_event.current_level, 6)

    def test_on_create__no_experience(self):
        with self.assertRaises(exceptions.OnEventCreateError):
            with self.concrete_event.on_create(self.emissary):
                pass

        self.assertEqual(self.concrete_event.transaction_id, None)
        self.assertEqual(self.concrete_event.current_level, None)

    def test_on_create__attribute_at_maximum(self):
        self.add_experience()

        @classmethod
        def experience_and_current_level(event_class, *argv, **kwargs):
            return event_class.PROPERTY.maximum, None

        with mock.patch('the_tale.game.emissaries.events.ClanLevelUpMixin.experience_and_current_level', experience_and_current_level):
            with self.assertRaises(exceptions.OnEventCreateError):
                with self.concrete_event.on_create(self.emissary):
                    pass

        self.assertEqual(self.concrete_event.transaction_id, None)
        self.assertEqual(self.concrete_event.current_level, None)

    def test_on_finish__already_level_upped(self):
        self.add_experience()

        self._set_attribute(3)

        with self.check_not_changed(self.get_experience):
            with self.check_decreased(self.get_experience):
                with self.concrete_event.on_create(self.emissary):
                    pass

            self._set_attribute(4)

            with self.check_increased(self.get_experience):
                self.assertFalse(self.concrete_event.on_finish(self.get_event()))

        attributes = clans_logic.load_attributes(self.emissary.clan_id)

        self.assertEqual(getattr(attributes, self.Event.PROPERTY.property), 4)

    def test_on_finish__already_at_maximum(self):
        self.add_experience()

        with self.check_not_changed(self.get_experience):
            with self.check_decreased(self.get_experience):
                with self.concrete_event.on_create(self.emissary):
                    pass

            self._set_attribute(self.Event.PROPERTY.maximum)
            self.concrete_event.current_value = self.Event.PROPERTY.maximum + 1

            with self.check_increased(self.get_experience):
                self.assertFalse(self.concrete_event.on_finish(self.get_event()))

        attributes = clans_logic.load_attributes(self.emissary.clan_id)

        self.assertEqual(getattr(attributes, self.Event.PROPERTY.property), self.Event.PROPERTY.maximum)

    def test_on_finish__success(self):
        self.add_experience()

        self._set_attribute(3)

        with self.concrete_event.on_create(self.emissary):
            pass

        self.assertTrue(self.concrete_event.on_finish(self.get_event()))

        attributes = clans_logic.load_attributes(self.emissary.clan_id)

        self.assertEqual(getattr(attributes, self.Event.PROPERTY.property), 4)

    def test_on_cancel(self):
        self.add_experience()

        self._set_attribute(3)

        with self.check_not_changed(self.get_experience):
            with self.check_decreased(self.get_experience):
                with self.concrete_event.on_create(self.emissary):
                    pass

            with self.check_increased(self.get_experience):
                self.concrete_event.on_cancel(self.get_event())

        attributes = clans_logic.load_attributes(self.emissary.clan_id)

        self.assertEqual(getattr(attributes, self.Event.PROPERTY.property), 3)

    def test_period_choices(self):
        self.assertEqual(len(self.concrete_event.period_choices(self.emissary)), 1)


class PointsGainLevelUpTests(ClanLevelUpMixin, utils_testcase.TestCase):
    Event = events.PointsGainLevelUp


class FightersMaximumLevelUpTests(ClanLevelUpMixin, utils_testcase.TestCase):
    Event = events.FightersMaximumLevelUp


class EmissariesMaximumLevelUpTests(ClanLevelUpMixin, utils_testcase.TestCase):
    Event = events.EmissariesMaximumLevelUp


class FreeQuestsMaximumLevelUpTests(ClanLevelUpMixin, utils_testcase.TestCase):
    Event = events.FreeQuestsMaximumLevelUp


class TrainingTests(BaseEventsMixin, utils_testcase.TestCase):

    Event = events.Training

    def setUp(self):
        super().setUp()

        self.concrete_event = self.Event(raw_ability_power=666)

    def test_event_description(self):
        self.assertEqual(self.concrete_event.effect_description(self.emissary, self.concrete_event.raw_ability_power),
                         self.concrete_event.event_description(self.emissary))

    def test_experience_per_step(self):
        self.assertEqual(self.concrete_event.experience_per_step(0), 21)
        self.assertEqual(self.concrete_event.experience_per_step(250), 23)
        self.assertEqual(self.concrete_event.experience_per_step(500), 24)
        self.assertEqual(self.concrete_event.experience_per_step(1000), 27)
        self.assertEqual(self.concrete_event.experience_per_step(2000), 32)

    def test_on_step(self):
        with self.check_delta(self.get_experience, self.concrete_event.experience_per_step(self.concrete_event.raw_ability_power)):
            self.concrete_event.on_step(self.get_event())


class ReservesSearchTests(BaseEventsMixin, utils_testcase.TestCase):

    Event = events.ReservesSearch

    def setUp(self):
        super().setUp()

        self.concrete_event = self.Event(raw_ability_power=666)

    def add_points(self, value):
        restrictions = clans_tt_services.currencies.Restrictions(hard_minimum=0,
                                                                 soft_maximum=tt_clans_constants.MAXIMUM_POINTS)

        clans_tt_services.currencies.cmd_change_balance(account_id=self.clan.id,
                                                        type='test',
                                                        amount=value,
                                                        asynchronous=False,
                                                        autocommit=True,
                                                        restrictions=restrictions,
                                                        currency=clans_relations.CURRENCY.ACTION_POINTS)

    def test_event_description(self):
        self.assertEqual(self.concrete_event.effect_description(self.emissary, self.concrete_event.raw_ability_power),
                         self.concrete_event.event_description(self.emissary))

    def test_pints_per_step(self):
        self.assertEqual(self.concrete_event.action_points_per_step(0), 20)
        self.assertEqual(self.concrete_event.action_points_per_step(250), 22)
        self.assertEqual(self.concrete_event.action_points_per_step(500), 23)
        self.assertEqual(self.concrete_event.action_points_per_step(1000), 26)
        self.assertEqual(self.concrete_event.action_points_per_step(2000), 31)

    def test_on_step(self):
        def get_action_points():
            return clans_tt_services.currencies.cmd_balance(self.clan.id, currency=clans_relations.CURRENCY.ACTION_POINTS)

        with self.check_delta(get_action_points, self.concrete_event.action_points_per_step(self.concrete_event.raw_ability_power)):
            self.concrete_event.on_step(self.get_event())

    def test_on_step__points_maximum(self):
        self.add_points(tt_clans_constants.MAXIMUM_POINTS)
        self.add_points(-7)

        def get_action_points():
            return clans_tt_services.currencies.cmd_balance(self.clan.id, currency=clans_relations.CURRENCY.ACTION_POINTS)

        with self.check_delta(get_action_points, 7):
            self.concrete_event.on_step(self.get_event())


class PlaceEffectEventMixin(BaseEventsMixin):
    ATTRIBUTE = NotImplemented

    def test_add_effect(self):

        self.assertEqual(self.concrete_event.effect_id, None)

        with self.check_delta(lambda: len(places_storage.effects.all()), 1):
            self.concrete_event.add_effect(self.get_event())

        effect = places_storage.effects.all()[0]

        self.assertEqual(self.concrete_event.effect_id, effect.id)

        self.assertEqual(effect.entity, self.emissary.place_id)
        self.assertEqual(effect.attribute, self.ATTRIBUTE)
        self.assertEqual(effect.value, self._get_expected_effect_value())
        self.assertEqual(effect.name, 'эмиссар [{}] {}'.format(self.clan.abbr, self.emissary.name))

    def test_add_effect__already_exists(self):
        self.concrete_event.add_effect(self.get_event())

        with self.check_not_changed(lambda: len(places_storage.effects.all())):
            self.concrete_event.add_effect(self.get_event())

    def test_remove_effect(self):
        self.concrete_event.add_effect(self.get_event())

        with self.check_delta(lambda: len(places_storage.effects.all()), -1):
            self.concrete_event.remove_effect(self.emissary)

    def test_remove_effect__already_removed(self):
        self.concrete_event.add_effect(self.get_event())

        self.concrete_event.remove_effect(self.emissary)

        self.concrete_event.remove_effect(self.emissary)

    def test_remove_effect__remove_before_create(self):
        self.assertEqual(self.concrete_event.effect_id, None)

        self.concrete_event.remove_effect(self.emissary)

    def test_on_cancel(self):
        self.concrete_event.add_effect(self.get_event())

        with self.check_delta(lambda: len(places_storage.effects.all()), -1):
            self.assertTrue(self.concrete_event.on_cancel(self.get_event()))

    def test_on_finish(self):
        self.concrete_event.add_effect(self.get_event())

        with self.check_delta(lambda: len(places_storage.effects.all()), -1):
            self.assertTrue(self.concrete_event.on_finish(self.get_event()))

    def test_on_step__effect_allowed_and_not_exists(self):
        self.concrete_event.remove_effect(self.emissary)

        with mock.patch.object(self.Event, 'is_effect_allowed', lambda self, emissary: True):
            with self.check_delta(lambda: len(places_storage.effects.all()), 1):
                self.concrete_event.on_step(self.get_event())

    def test_on_step__effect_allowed_and_exists(self):
        self.concrete_event.add_effect(self.get_event())

        with mock.patch.object(self.Event, 'is_effect_allowed', lambda self, emissary: True):
            with self.check_not_changed(lambda: len(places_storage.effects.all())):
                self.concrete_event.on_step(self.get_event())

    def test_on_step__effect_not_allowed_and_exists(self):
        self.concrete_event.add_effect(self.get_event())

        with mock.patch.object(self.Event, 'is_effect_allowed', lambda self, emissary: False):
            with self.check_delta(lambda: len(places_storage.effects.all()), -1):
                self.concrete_event.on_step(self.get_event())

    def test_on_step__effect_not_allowed_and_not_exists(self):
        self.concrete_event.remove_effect(self.emissary)

        with mock.patch.object(self.Event, 'is_effect_allowed', lambda self, emissary: False):
            with self.check_not_changed(lambda: len(places_storage.effects.all())):
                self.concrete_event.on_step(self.get_event())


class CountedEventMixin:

    EVENT_CURRENCY = NotImplemented

    def test_tokens_per_day(self):
        self.assertEqual(self.concrete_event.tokens_per_day(0), 3)
        self.assertEqual(self.concrete_event.tokens_per_day(250), 3.24)
        self.assertEqual(self.concrete_event.tokens_per_day(500), 3.48)
        self.assertEqual(self.concrete_event.tokens_per_day(1000), 3.96)
        self.assertEqual(self.concrete_event.tokens_per_day(2000), 4.92)
        self.assertEqual(self.concrete_event.tokens_per_day(10000), 12.6)

    def test_points_per_step(self):
        self.assertEqual(self.concrete_event.points_per_step(), 152)

    def test_change_points(self):
        with self.check_delta(self.get_event_points, self.concrete_event.points_per_step()):
            self.concrete_event.change_points(self.emissary, amount=self.concrete_event.points_per_step())

    def give_currency_points(self, amount):
        tt_services.events_currencies.cmd_change_balance(account_id=self.concrete_event.resource_id(self.emissary),
                                                         type='test',
                                                         amount=amount,
                                                         asynchronous=False,
                                                         autocommit=True,
                                                         currency=self.EVENT_CURRENCY)


class CountedPlaceEventsMixin(CountedEventMixin, PlaceEffectEventMixin):

    Event = NotImplemented

    def setUp(self):
        places_tt_services.effects.cmd_debug_clear_service()

        super().setUp()

        tt_services.events_currencies.cmd_debug_clear_service()

        self.concrete_event = self.Event(raw_ability_power=666)

    def _get_expected_effect_value(self):
        return self.emissary.clan_id

    def test_after_create(self):
        with self.check_delta(lambda: len(places_storage.effects.all()), 1):
            with self.check_delta(self.get_event_points, tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
                self.concrete_event.after_create(self.get_event())

    def test_on_step__enough_currency(self):
        self.assertEqual(self.concrete_event.effect_id, None)

        self.give_currency_points(tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER - 1)

        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

        with self.check_delta(lambda: len(places_storage.effects.all()), 1):
            self.concrete_event.on_step(self.get_event())

        self.assertTrue(self.concrete_event.is_effect_allowed(self.emissary))

    def test_on_step__not_enough_currency(self):
        self.assertEqual(self.concrete_event.effect_id, None)

        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

        with self.check_not_changed(lambda: len(places_storage.effects.all())):
            self.assertTrue(self.concrete_event.on_step(self.get_event()))

        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

    def test_on_monitoring(self):
        self.assertEqual(self.concrete_event.effect_id, None)

        self.give_currency_points(tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER - 1)

        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

        with self.check_not_changed(self.get_event_points):
            with self.check_not_changed(lambda: len(places_storage.effects.all())):
                self.concrete_event.on_monitoring(self.get_event())

        self.give_currency_points(1)

        self.assertTrue(self.concrete_event.is_effect_allowed(self.emissary))

        with self.check_not_changed(self.get_event_points):
            with self.check_delta(lambda: len(places_storage.effects.all()), 1):
                self.concrete_event.on_monitoring(self.get_event())

        self.give_currency_points(-1)

        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

        with self.check_not_changed(self.get_event_points):
            with self.check_delta(lambda: len(places_storage.effects.all()), -1):
                self.concrete_event.on_monitoring(self.get_event())

    def test_is_effect_allowed(self):

        self.concrete_event.after_create(self.get_event())

        self.assertTrue(self.concrete_event.is_effect_allowed(self.emissary))

        self.concrete_event.change_points(self.emissary, amount=-100500)

        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

        self.concrete_event.change_points(self.emissary, amount=100501)

        self.assertTrue(self.concrete_event.is_effect_allowed(self.emissary))


class TaskBoardUpdatingTests(CountedPlaceEventsMixin, utils_testcase.TestCase):

    Event = events.TaskBoardUpdating
    EVENT_CURRENCY = relations.EVENT_CURRENCY.TASK_BOARD
    ATTRIBUTE = places_relations.ATTRIBUTE.TASK_BOARD

    def test_tokens_per_day(self):
        self.assertEqual(self.concrete_event.tokens_per_day(0), 5.0)
        self.assertEqual(self.concrete_event.tokens_per_day(250), 5.4)
        self.assertEqual(self.concrete_event.tokens_per_day(500), 5.8)
        self.assertEqual(self.concrete_event.tokens_per_day(1000), 6.6)
        self.assertEqual(self.concrete_event.tokens_per_day(2000), 8.2)
        self.assertEqual(self.concrete_event.tokens_per_day(10000), 21.0)

    def test_points_per_step(self):
        self.assertEqual(self.concrete_event.points_per_step(), 253)


class FastTransportationTests(CountedPlaceEventsMixin, utils_testcase.TestCase):

    Event = events.FastTransportation
    EVENT_CURRENCY = relations.EVENT_CURRENCY.FAST_TRANSPORTATION
    ATTRIBUTE = places_relations.ATTRIBUTE.FAST_TRANSPORTATION


class CompanionsSupportTests(CountedPlaceEventsMixin, utils_testcase.TestCase):

    Event = events.CompanionsSupport
    EVENT_CURRENCY = relations.EVENT_CURRENCY.COMPANIONS_SUPPORT
    ATTRIBUTE = places_relations.ATTRIBUTE.COMPANIONS_SUPPORT


class PlaceEffectDirectInfluenceMixin(PlaceEffectEventMixin):

    def setUp(self):
        places_tt_services.effects.cmd_debug_clear_service()

        super().setUp()

        self.concrete_event = self.Event(raw_ability_power=666)

    def _get_expected_effect_value(self):
        return self.concrete_event.direct_effect_value(self.concrete_event.raw_ability_power)

    def test_is_effect_allowed(self):
        self.emissary.place_rating_position = None
        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

        self.emissary.place_rating_position = 0
        self.assertTrue(self.concrete_event.is_effect_allowed(self.emissary))

        self.emissary.place_rating_position = tt_emissaries_constants.PLACE_LEADERS_NUMBER - 1
        self.assertTrue(self.concrete_event.is_effect_allowed(self.emissary))

        self.emissary.place_rating_position = tt_emissaries_constants.PLACE_LEADERS_NUMBER
        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

    def test_after_create__effect_not_allowed(self):
        with mock.patch.object(self.Event, 'is_effect_allowed', lambda self, emissary: False):
            with self.check_not_changed(lambda: len(places_storage.effects.all())):
                self.concrete_event.after_create(self.get_event())

    def test_after_create__effect_allowed(self):
        with mock.patch.object(self.Event, 'is_effect_allowed', lambda self, emissary: True):
            with self.check_delta(lambda: len(places_storage.effects.all()), 1):
                self.concrete_event.after_create(self.get_event())


class ArtisansSupportTests(PlaceEffectDirectInfluenceMixin, utils_testcase.TestCase):
    Event = events.ArtisansSupport
    ATTRIBUTE = places_relations.ATTRIBUTE.PRODUCTION

    def test_effect_value(self):
        self.concrete_event.raw_ability_power = 0
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 25)

        self.concrete_event.raw_ability_power = 1000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 39)

        self.concrete_event.raw_ability_power = 5000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 95)


class PublicOpinionManagementTests(PlaceEffectDirectInfluenceMixin, utils_testcase.TestCase):
    Event = events.PublicOpinionManagement
    ATTRIBUTE = places_relations.ATTRIBUTE.STABILITY

    def test_effect_value(self):
        self.concrete_event.raw_ability_power = 0
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.025)

        self.concrete_event.raw_ability_power = 1000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.039)

        self.concrete_event.raw_ability_power = 5000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.095)


class PatronageTests(PlaceEffectDirectInfluenceMixin, utils_testcase.TestCase):
    Event = events.Patronage
    ATTRIBUTE = places_relations.ATTRIBUTE.CULTURE

    def test_effect_value(self):
        self.concrete_event.raw_ability_power = 0
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.0375)

        self.concrete_event.raw_ability_power = 1000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.0585)

        self.concrete_event.raw_ability_power = 5000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.1425)


class PatrioticPatronageTests(PlaceEffectDirectInfluenceMixin, utils_testcase.TestCase):
    Event = events.PatrioticPatronage
    RACE = game_relations.RACE.random()
    ATTRIBUTE = getattr(places_relations.ATTRIBUTE, 'DEMOGRAPHICS_PRESSURE_{}'.format(RACE.name))

    def setUp(self):
        super().setUp()
        self.emissary.race = self.RACE

    def test_effect_value(self):
        self.concrete_event.raw_ability_power = 0
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.25)

        self.concrete_event.raw_ability_power = 1000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.39)

        self.concrete_event.raw_ability_power = 5000
        self.assertEqual(self.concrete_event._effect_value(self.get_event()), 0.95)


class GloryOfTheKeepersTests(CountedEventMixin,
                             BaseEventsMixin,
                             utils_testcase.TestCase):
    Event = events.GloryOfTheKeepers
    EVENT_CURRENCY = relations.EVENT_CURRENCY.GLORY_OF_THE_KEEPERS

    def setUp(self):
        tt_services.events_currencies.cmd_debug_clear_service()

        super().setUp()

        self.concrete_event = self.Event(raw_ability_power=666)

    def test_tokens_per_day(self):
        self.assertEqual(self.concrete_event.tokens_per_day(0), 1)
        self.assertEqual(self.concrete_event.tokens_per_day(250), 1.08)
        self.assertEqual(self.concrete_event.tokens_per_day(500), 1.16)
        self.assertEqual(self.concrete_event.tokens_per_day(1000), 1.32)
        self.assertEqual(self.concrete_event.tokens_per_day(2000), 1.64)
        self.assertEqual(self.concrete_event.tokens_per_day(10000), 4.2)

    def test_points_per_step(self):
        self.assertEqual(self.concrete_event.points_per_step(), 51)

    def test_is_effect_allowed(self):

        self.concrete_event.after_create(self.get_event())

        self.assertFalse(self.concrete_event.is_effect_allowed(self.emissary))

        self.concrete_event.change_points(self.emissary, amount=100501)

        self.assertTrue(self.concrete_event.is_effect_allowed(self.emissary))

    def test_on_step__effect_not_allowed(self):

        with self.check_increased(self.get_event_points):
            with self.check_not_changed(lambda: cards_tt_services.storage.cmd_get_items(self.account.id)):
                self.concrete_event.on_step(self.get_event())

    def test_on_step__single_effect(self):

        self.give_currency_points(tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER - 1)

        with self.check_delta(self.get_event_points,
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER + self.concrete_event.points_per_step() ):
            with self.check_delta(lambda: len(cards_tt_services.storage.cmd_get_items(self.account.id)), 1):
                with self.check_delta(lambda: personal_messages_tt_services.personal_messages.cmd_new_messages_number(self.account.id), 1):
                    self.concrete_event.on_step(self.get_event())

    def test_on_step__multiple_effects(self):
        self.give_currency_points(tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER * 2 - 1)

        with self.check_delta(self.get_event_points,
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER * 2 + self.concrete_event.points_per_step() ):
            with self.check_delta(lambda: len(cards_tt_services.storage.cmd_get_items(self.account.id)), 2):
                with self.check_delta(lambda: personal_messages_tt_services.personal_messages.cmd_new_messages_number(self.account.id), 2):
                    self.concrete_event.on_step(self.get_event())

    def test_on_step__multiple_accounts(self):
        account_2 = self.accounts_factory.create_account()
        account_3 = self.accounts_factory.create_account()

        clans_logic._add_member(clan=self.clan,
                                account=account_2,
                                role=clans_relations.MEMBER_ROLE.OFFICER)

        N = 20

        self.give_currency_points(tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER * N)

        with self.check_delta(self.get_event_points,
                              -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER * N + self.concrete_event.points_per_step() ):
            with self.check_increased(lambda: len(cards_tt_services.storage.cmd_get_items(self.account.id))):
                with self.check_increased(lambda: len(cards_tt_services.storage.cmd_get_items(account_2.id))):
                    with self.check_not_changed(lambda: len(cards_tt_services.storage.cmd_get_items(account_3.id))):
                        self.concrete_event.on_step(self.get_event())
