
import smart_imports

smart_imports.all()


class LogicTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicTests, self).setUp()

        logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

    def test_remove_game_data(self):

        self.assertEqual(heroes_models.Hero.objects.count(), 1)

        logic.remove_game_data(self.account)

        self.assertEqual(heroes_models.Hero.objects.count(), 0)


class FormGameInfoTests(pvp_helpers.PvPTestsMixin, utils_testcase.TestCase):

    def setUp(self):
        super(FormGameInfoTests, self).setUp()

        logic.create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        pvp_tt_services.matchmaker.cmd_debug_clear_service()

    def test_no_account(self):
        data = logic.form_game_info()
        self.assertEqual(data['mode'], 'pve')
        self.assertEqual(data['account'], None)
        self.assertEqual(data['enemy'], None)

    def test_account(self):
        data = logic.form_game_info(self.account_1, is_own=True)
        self.assertEqual(data['mode'], 'pve')
        self.assertEqual(data['account']['id'], self.account_1.id)
        self.assertEqual(data['enemy'], None)

    def test_account__other(self):
        data = logic.form_game_info(self.account_2, is_own=True)
        self.assertEqual(data['mode'], 'pve')
        self.assertEqual(data['account']['id'], self.account_2.id)
        self.assertEqual(data['enemy'], None)

    def test_pvp(self):
        self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)

        data = logic.form_game_info(self.account_1)

        self.assertEqual(data['mode'], 'pvp')

        self.assertTrue(data['account']['hero']['action']['data']['is_pvp'])
        self.assertTrue(data['enemy']['hero']['action']['data']['is_pvp'])

        self.assertEqual(data['account']['hero']['action']['data']['enemy_id'], self.account_2.id)
        self.assertEqual(data['enemy']['hero']['action']['data']['enemy_id'], self.account_1.id)

        self.assertEqual(data['account']['id'], self.account_1.id)
        self.assertEqual(data['enemy']['id'], self.account_2.id)

    def test_own_hero_get_cached_data(self):
        hero = heroes_logic.load_hero(account_id=self.account_1.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.cached_ui_info_for_hero',
                        mock.Mock(return_value={'actual_on_turn': hero.saved_at_turn,
                                                'pvp': 'actual',
                                                'action': {},
                                                'ui_caching_started_at': 0})) as cached_ui_info_for_hero:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info') as ui_info:
                data = logic.form_game_info(self.account_1, is_own=True)

        self.assertEqual(data['account']['hero']['pvp'], 'actual')
        self.assertEqual(data['enemy'], None)

        self.assertEqual(cached_ui_info_for_hero.call_count, 1)
        self.assertEqual(cached_ui_info_for_hero.call_args, mock.call(account_id=self.account_1.id, recache_if_required=True, patch_turns=None, for_last_turn=False))
        self.assertEqual(ui_info.call_count, 0)

    def create_not_own_ui_info(self, hero, enemy_id=None):
        pvp_data = None

        if enemy_id is not None:
            pvp_data = {'is_pvp': True,
                        'enemy_id': enemy_id,
                        'pvp__actual': 'actual',
                        'pvp__last_turn': 'last_turn'}

        return {'actual_on_turn': hero.saved_at_turn,
                'action': {'data': pvp_data},
                'ui_caching_started_at': 0,
                'changed_fields': []}

    def test_not_own_hero_get_cached_data__not_cached(self):
        hero = heroes_logic.load_hero(account_id=self.account_1.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.cached_ui_info_for_hero',
                        mock.Mock(return_value=self.create_not_own_ui_info(hero, enemy_id=self.account_2.id))) as cached_ui_info_for_hero:
            with mock.patch('the_tale.game.heroes.objects.Hero.ui_info',
                            mock.Mock(return_value=self.create_not_own_ui_info(hero, enemy_id=self.account_2.id))) as ui_info:
                logic.form_game_info(self.account_1, is_own=False)

        self.assertEqual(cached_ui_info_for_hero.call_count, 2)
        self.assertEqual(cached_ui_info_for_hero.call_args_list,
                         [mock.call(account_id=self.account_1.id, recache_if_required=False, patch_turns=None, for_last_turn=True),
                          mock.call(account_id=self.account_2.id, recache_if_required=False, patch_turns=None, for_last_turn=True)])
        self.assertEqual(ui_info.call_count, 0)

    @mock.patch.object(utils_cache, 'get', lambda *argv, **kwargs: None)
    def test_not_own_hero_get_cached_data(self):
        battle_info = self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)

        with mock.patch('the_tale.game.heroes.objects.Hero.ui_info',
                        lambda *argv, **kwargs: self.create_not_own_ui_info(battle_info.hero_1,
                                                                            enemy_id=battle_info.hero_2.id)):
            data = logic.form_game_info(self.account_1, is_own=False)

        self.assertEqual(data['account']['hero']['action']['data']['pvp'], 'last_turn')
        self.assertEqual(data['enemy']['hero']['action']['data']['pvp'], 'last_turn')

        self.assertFalse('pvp__actual' in data['account']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__last_turn' in data['account']['hero']['action']['data']['pvp'])

        self.assertFalse('pvp__actual' in data['enemy']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__last_turn' in data['enemy']['hero']['action']['data']['pvp'])

    def test_is_old(self):
        self.assertFalse(logic.form_game_info(self.account_1, is_own=True)['account']['is_old'])

        game_turn.set(666)
        self.assertTrue(logic.form_game_info(self.account_1, is_own=True)['account']['is_old'])

        heroes_logic.save_hero(heroes_logic.load_hero(account_id=self.account_1.id))
        self.assertFalse(logic.form_game_info(self.account_1, is_own=True)['account']['is_old'])

    def test_is_old__not_own_hero(self):
        self.assertFalse(logic.form_game_info(self.account_1, is_own=False)['account']['is_old'])

        game_turn.set(666)

        self.assertTrue(logic.form_game_info(self.account_1, is_own=False)['account']['is_old'])

        heroes_logic.save_hero(heroes_logic.load_hero(account_id=self.account_1.id))
        self.assertFalse(logic.form_game_info(self.account_1, is_own=False)['account']['is_old'])

    def test_is_old__pvp(self):
        battle_info = self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)

        self.assertFalse(logic.form_game_info(self.account_1)['account']['is_old'])
        self.assertFalse(logic.form_game_info(self.account_1)['enemy']['is_old'])

        game_turn.set(666)

        self.assertTrue(logic.form_game_info(self.account_1)['account']['is_old'])
        self.assertTrue(logic.form_game_info(self.account_1)['enemy']['is_old'])

        battle_info.storage.save_changed_data()

        self.assertFalse(logic.form_game_info(self.account_1)['account']['is_old'])
        self.assertFalse(logic.form_game_info(self.account_1)['enemy']['is_old'])

    def test_game_info_data_hidding(self):
        '''
        player hero always must show actual data
        enemy hero always must show data on statrt of the turn
        '''
        battle_info = self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)

        hero_1_pvp, hero_2_pvp = pvp_logic.get_arena_heroes_pvp(battle_info.hero_1)

        hero_1_pvp.set_energy(1)
        hero_2_pvp.set_energy(2)

        battle_info.storage.save_all()

        heroes_objects.Hero.reset_ui_cache(self.account_1.id)
        heroes_objects.Hero.reset_ui_cache(self.account_2.id)

        data = logic.form_game_info(battle_info.account_1, is_own=True)

        self.assertEqual(data['account']['hero']['action']['data']['pvp']['energy'], 1)
        self.assertEqual(data['enemy']['hero']['action']['data']['pvp']['energy'], 0)

        hero_2_pvp.store_turn_data()

        battle_info.storage.save_changed_data()

        data = logic.form_game_info(battle_info.account_1, is_own=True)

        self.assertEqual(data['enemy']['hero']['action']['data']['pvp']['energy'], 2)

    @mock.patch.object(utils_cache, 'get', lambda *argv, **kwargs: None)
    def test_game_info_caching(self):
        battle_info = self.create_pvp_battle(account_1=self.account_1, account_2=self.account_2)

        def get_ui_info(hero, **kwargs):
            if hero.id == battle_info.hero_1.id:
                return {'actual_on_turn': battle_info.hero_1.saved_at_turn,
                        'action': {'data': {'is_pvp': True,
                                            'enemy_id': battle_info.hero_2.id,
                                            'pvp__actual': 'actual',
                                            'pvp__last_turn': 'last_turn'}},
                        'changed_fields': [],
                        'ui_caching_started_at': 0}
            else:
                return self.create_not_own_ui_info(battle_info.hero_2, enemy_id=self.account_1.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.ui_info', get_ui_info):
            data = logic.form_game_info(self.account_1, is_own=True)

        self.assertEqual(data['account']['hero']['action']['data']['pvp'], 'actual')
        self.assertEqual(data['enemy']['hero']['action']['data']['pvp'], 'last_turn')

        self.assertFalse('pvp__actual' in data['account']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__last_turn' in data['account']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__actual' in data['enemy']['hero']['action']['data']['pvp'])
        self.assertFalse('pvp__last_turn' in data['enemy']['hero']['action']['data']['pvp'])

        self.assertEqual(data['enemy']['energy'], None)


class HighlevelStepTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.places = logic.create_test_map()

    def test_places_methods_called(self):
        # all that methods tested in places package
        set_power_economic = mock.Mock()
        sync_size = mock.Mock()
        sync_habits = mock.Mock()
        refresh_attributes = mock.Mock()
        mark_as_updated = mock.Mock()
        set_area = mock.Mock()
        sync_race = mock.Mock()
        update_heroes_habits = mock.Mock()

        with mock.patch('the_tale.game.places.attributes.Attributes.set_power_economic', set_power_economic), \
                mock.patch('the_tale.game.places.attributes.Attributes.sync_size', sync_size), \
                mock.patch('the_tale.game.places.attributes.Attributes.set_area', set_area), \
                mock.patch('the_tale.game.places.objects.Place.sync_habits', sync_habits), \
                mock.patch('the_tale.game.places.objects.Place.sync_race', sync_race), \
                mock.patch('the_tale.game.places.objects.Place.refresh_attributes', refresh_attributes), \
                mock.patch('the_tale.game.places.objects.Place.update_heroes_habits', update_heroes_habits), \
                mock.patch('the_tale.game.places.objects.Place.mark_as_updated', mark_as_updated):
            logic.highlevel_step(logger=mock.Mock())

        places_number = len(places_storage.places.all())

        for method in (set_power_economic,
                       sync_size,
                       sync_habits,
                       refresh_attributes,
                       mark_as_updated,
                       set_area,
                       sync_race,
                       update_heroes_habits):
            self.assertEqual(method.call_count, places_number)

    def give_power_to_person(self, person, power, fame):
        impacts = persons_logic.tt_power_impacts(person_inner_circle=False,
                                                 place_inner_circle=False,
                                                 actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                 actor_id=666,
                                                 person=person,
                                                 amount=power,
                                                 fame=fame)

        politic_power_logic.add_power_impacts(impacts)

    def give_power_to_place(self, place, power, fame):
        impacts = places_logic.tt_power_impacts(inner_circle=False,
                                                actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                actor_id=666,
                                                place=place,
                                                amount=power,
                                                fame=fame)
        politic_power_logic.add_power_impacts(impacts)

    @mock.patch('tt_logic.politic_power.constants.POWER_REDUCE_FRACTION', 0.9)
    @mock.patch('the_tale.game.persons.attributes.Attributes.places_help_amount', 1)
    @mock.patch('the_tale.game.places.attributes.Attributes.freedom', 1)
    @mock.patch('the_tale.game.places.objects.Place.refresh_attributes', mock.Mock())
    def test_sync_data(self):
        game_tt_services.debug_clear_service()

        self.assertEqual(politic_power_storage.places.outer_power(self.places[0].id), 0)
        self.assertEqual(politic_power_storage.places.inner_power(self.places[0].id), 0)
        self.assertEqual(politic_power_storage.places.outer_power(self.places[1].id), 0)
        self.assertEqual(politic_power_storage.places.inner_power(self.places[1].id), 0)
        self.assertEqual(politic_power_storage.places.outer_power(self.places[2].id), 0)
        self.assertEqual(politic_power_storage.places.inner_power(self.places[2].id), 0)

        self.assertEqual(persons_models.Person.objects.filter(place_id=self.places[0].id).count(), 3)
        self.assertEqual(persons_models.Person.objects.filter(place_id=self.places[1].id).count(), 3)
        self.assertEqual(persons_models.Person.objects.filter(place_id=self.places[2].id).count(), 3)
        self.assertEqual(len(persons_storage.persons.all()), 9)

        popularity = places_logic.get_hero_popularity(666)

        self.assertEqual(popularity.get_fame(self.places[0].id), 0)
        self.assertEqual(popularity.get_fame(self.places[1].id), 0)
        self.assertEqual(popularity.get_fame(self.places[2].id), 0)

        person_1_1 = self.places[0].persons[0]
        person_2_1, person_2_2 = self.places[1].persons[0:2]
        person_3_1, person_3_2 = self.places[2].persons[0:2]

        self.give_power_to_person(person=person_1_1, power=1, fame=2)
        self.give_power_to_person(person=person_2_1, power=100, fame=200)
        self.give_power_to_person(person=person_2_2, power=1000, fame=2000)
        self.give_power_to_person(person=person_3_1, power=10000, fame=20000)
        self.give_power_to_person(person=person_3_2, power=100000, fame=200000)

        with self.check_changed(lambda: persons_storage.persons._version):
            with self.check_changed(lambda: places_storage.places._version):
                logic.highlevel_step(logger=mock.Mock())

        self.assertTrue(self.places[0]._modifier.is_NONE)

        game_turn.increment()

        self.assertEqual(politic_power_storage.persons.outer_power(person_1_1.id), 0)
        self.assertEqual(politic_power_storage.persons.outer_power(person_2_1.id), 90)
        self.assertEqual(politic_power_storage.persons.outer_power(person_2_2.id), 900)
        self.assertEqual(politic_power_storage.persons.outer_power(person_3_1.id), 9000)
        self.assertEqual(politic_power_storage.persons.outer_power(person_3_2.id), 90000)

        self.assertEqual(politic_power_storage.places.outer_power(self.places[0].id), 0)
        self.assertEqual(politic_power_storage.places.outer_power(self.places[1].id), 990)
        self.assertEqual(politic_power_storage.places.outer_power(self.places[2].id), 99000)

        popularity = places_logic.get_hero_popularity(666)

        self.assertEqual(popularity.get_fame(self.places[0].id), 1)
        self.assertEqual(popularity.get_fame(self.places[1].id), 2189)
        self.assertEqual(popularity.get_fame(self.places[2].id), 218997)

        self.give_power_to_place(place=self.places[0], power=-10, fame=-20)
        self.give_power_to_place(place=self.places[1], power=-1, fame=-2)
        self.give_power_to_place(place=self.places[1], power=+10000000, fame=20000000)
        self.give_power_to_place(place=self.places[2], power=-2, fame=-40)
        self.give_power_to_place(place=self.places[2], power=+20, fame=40)

        with self.check_changed(lambda: persons_storage.persons._version):
            with self.check_changed(lambda: places_storage.places._version):
                logic.highlevel_step(logger=mock.Mock())

        self.places = [places_storage.places[self.places[0].id],
                       places_storage.places[self.places[1].id],
                       places_storage.places[self.places[2].id]]

        self.assertEqual(politic_power_storage.places.outer_power(self.places[0].id), -9)
        self.assertEqual(politic_power_storage.places.outer_power(self.places[1].id), 9000890)
        self.assertEqual(politic_power_storage.places.outer_power(self.places[2].id), 89116)

        popularity = places_logic.get_hero_popularity(666)

        self.assertEqual(popularity.get_fame(self.places[0].id), 0)
        self.assertEqual(popularity.get_fame(self.places[1].id), 19911015)
        self.assertEqual(popularity.get_fame(self.places[2].id), 218038)
