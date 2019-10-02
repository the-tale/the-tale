
import smart_imports

smart_imports.all()


class BaseEmissaryTests(utils_testcase.TestCase,
                        clans_helpers.ClansTestsMixin,
                        helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        clans_tt_services.chronicle.cmd_debug_clear_service()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

        self.hero = heroes_logic.load_hero(account_id=self.account.id)


class CreateEmissaryTests(BaseEmissaryTests):

    def test(self):
        name = game_names.generator().get_test_name('emissary')

        game_turn.increment(delta=666)

        with self.check_changed(lambda: storage.emissaries.version):
            emissary = logic.create_emissary(initiator=self.account,
                                             clan=self.clan,
                                             place_id=self.places[0].id,
                                             gender=game_relations.GENDER.FEMALE,
                                             race=game_relations.RACE.GOBLIN,
                                             utg_name=name)

        self.assertEqual(emissary.clan_id, self.clan.id)
        self.assertEqual(emissary.place_id, self.places[0].id)
        self.assertTrue(emissary.gender.is_FEMALE)
        self.assertTrue(emissary.race.is_GOBLIN)
        self.assertEqual(emissary.utg_name, name)
        self.assertTrue(emissary.state.is_IN_GAME)
        self.assertTrue(emissary.remove_reason.is_NOT_REMOVED)
        self.assertEqual(emissary.created_at_turn, game_turn.number())
        self.assertEqual(emissary.updated_at_turn, game_turn.number())
        self.assertEqual(emissary.moved_at_turn, game_turn.number())

        loaded_emissary = logic.load_emissary(emissary.id)

        self.assertEqual(emissary, loaded_emissary)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_CREATED.meta_object().tag,
                          self.account.meta_object().tag,
                          emissary.meta_object().tag})

        power = politic_power_logic.get_emissaries_power([emissary.id])[emissary.id]

        self.assertEqual(power, tt_clans_constants.INITIAL_EMISSARY_POWER)


class LoadEmissariesForClanTests(BaseEmissaryTests):

    def test_no_emissaries(self):
        emissaries = logic.load_emissaries_for_clan(self.clan.id)
        self.assertEqual(emissaries, [])

    def test_all_emissaries(self):

        emissaries = [self.create_emissary(clan=self.clan,
                                           initiator=self.account,
                                           place_id=random.choice(self.places).id)
                      for i in range(10)]

        emissaries.sort(key=lambda emissary: emissary.id)

        logic._remove_emissary(emissaries[4].id, reason=relations.REMOVE_REASON.KILLED)
        logic._remove_emissary(emissaries[6].id, reason=relations.REMOVE_REASON.DISMISSED)

        other_account = self.accounts_factory.create_account()
        other_clan = self.create_clan(owner=other_account, uid=2)

        self.create_emissary(clan=other_clan,
                             initiator=other_account,
                             place_id=random.choice(self.places).id)

        loaded_emissaries = logic.load_emissaries_for_clan(self.clan.id)

        loaded_emissaries.sort(key=lambda emissary: emissary.id)

        self.assertTrue(loaded_emissaries[4].state.is_OUT_GAME)
        self.assertTrue(loaded_emissaries[6].state.is_OUT_GAME)

        loaded_emissaries[4] = emissaries[4]
        loaded_emissaries[6] = emissaries[6]

        self.assertEqual(emissaries, loaded_emissaries)


class LoadEmissariesForPlaceTests(BaseEmissaryTests):

    def test_no_emissaries(self):
        emissaries = logic.load_emissaries_for_place(self.places[0].id)
        self.assertEqual(emissaries, [])

    def test_all_emissaries(self):

        other_account = self.accounts_factory.create_account()
        other_clan = self.create_clan(owner=other_account, uid=2)

        emissaries = [self.create_emissary(clan=random.choice((self.clan, other_clan)),
                                           initiator=self.account,
                                           place_id=self.places[i % 3].id)
                      for i in range(10)]

        emissaries.sort(key=lambda emissary: emissary.id)

        logic._remove_emissary(emissaries[4].id, reason=relations.REMOVE_REASON.KILLED)
        logic._remove_emissary(emissaries[6].id, reason=relations.REMOVE_REASON.DISMISSED)

        loaded_emissaries = logic.load_emissaries_for_place(self.places[0].id)

        loaded_emissaries.sort(key=lambda emissary: emissary.id)

        self.assertEqual(len(loaded_emissaries), 4)

        self.assertEqual([emissaries[0].id,
                          emissaries[3].id,
                          emissaries[6].id,
                          emissaries[9].id],
                         [emissary.id for emissary in loaded_emissaries])


class RemoveEmissaryTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        other_account = self.accounts_factory.create_account()
        other_clan = self.create_clan(owner=other_account, uid=2)

        self.emissaries = [self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id),
                           self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id),
                           self.create_emissary(clan=other_clan,
                                                initiator=other_account,
                                                place_id=random.choice(self.places).id)]

    def test_simple(self):

        game_turn.increment(delta=100)

        with self.check_changed(lambda: storage.emissaries.version):
            logic._remove_emissary(emissary_id=self.emissaries[1].id,
                                   reason=relations.REMOVE_REASON.DISMISSED)

        loaded_emissaries = [logic.load_emissary(emissary_id=emissary.id)
                             for emissary in self.emissaries]

        self.assertTrue(loaded_emissaries[0].state.is_IN_GAME)
        self.assertTrue(loaded_emissaries[0].remove_reason.is_NOT_REMOVED)

        self.assertTrue(loaded_emissaries[1].state.is_OUT_GAME)
        self.assertTrue(loaded_emissaries[1].remove_reason.is_DISMISSED)

        self.assertEqual(loaded_emissaries[1].created_at_turn, loaded_emissaries[0].created_at_turn)
        self.assertEqual(loaded_emissaries[1].updated_at_turn, game_turn.number())
        self.assertEqual(loaded_emissaries[1].moved_at_turn, loaded_emissaries[0].moved_at_turn)

        self.assertTrue(loaded_emissaries[2].state.is_IN_GAME)
        self.assertTrue(loaded_emissaries[2].remove_reason.is_NOT_REMOVED)


class DismissEmissaryTests(BaseEmissaryTests):

    def test(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=random.choice(self.places).id)

        logic.dismiss_emissary(initiator=self.account,
                               emissary_id=emissary.id)

        loaded_emissary = logic.load_emissary(emissary_id=emissary.id)

        self.assertTrue(loaded_emissary.state.is_OUT_GAME)
        self.assertTrue(loaded_emissary.remove_reason.is_DISMISSED)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_DISSMISSED.meta_object().tag,
                          self.account.meta_object().tag,
                          emissary.meta_object().tag})


class KillEmissaryTests(BaseEmissaryTests):

    def test(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=random.choice(self.places).id)

        logic.kill_emissary(emissary_id=emissary.id)

        loaded_emissary = logic.load_emissary(emissary_id=emissary.id)

        self.assertTrue(loaded_emissary.state.is_OUT_GAME)
        self.assertTrue(loaded_emissary.remove_reason.is_KILLED)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_KILLED.meta_object().tag,
                          emissary.meta_object().tag})


class DamageEmissaryTests(BaseEmissaryTests):

    def test(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=random.choice(self.places).id)

        self.assertEqual(emissary.health, emissary.max_health)

        logic.damage_emissary(emissary_id=emissary.id)

        loaded_emissary = logic.load_emissary(emissary_id=emissary.id)

        self.assertEqual(loaded_emissary.health, loaded_emissary.max_health - 1)
        self.assertTrue(loaded_emissary.state.is_IN_GAME)

        self.assertEqual(emissary.health, emissary.max_health - 1)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_DAMAGED.meta_object().tag,
                          emissary.meta_object().tag})

    def test_already_zero_health(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=random.choice(self.places).id)

        emissary.health = 0

        logic.damage_emissary(emissary_id=emissary.id)

        loaded_emissary = logic.load_emissary(emissary_id=emissary.id)

        self.assertEqual(loaded_emissary.health, 0)
        self.assertTrue(loaded_emissary.state.is_IN_GAME)

        self.assertEqual(emissary.health, 0)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_DAMAGED.meta_object().tag,
                          emissary.meta_object().tag})


class DamageEmissariesTests(BaseEmissaryTests):

    def test(self):
        for i in range(3):
            self.create_emissary(clan=self.clan,
                                 initiator=self.account,
                                 place_id=random.choice(self.places).id)

        emissaries = list(storage.emissaries.all())

        politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=666,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                            target_id=emissaries[0].id,
                                                                            amount=10000),
                                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=666,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                            target_id=emissaries[1].id,
                                                                            amount=-tt_clans_constants.INITIAL_EMISSARY_POWER),
                                                game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=666,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                            target_id=emissaries[2].id,
                                                                            amount=-tt_clans_constants.INITIAL_EMISSARY_POWER-1000)])

        logic.damage_emissaries()

        self.assertEqual(storage.emissaries[emissaries[0].id].health,
                         storage.emissaries[emissaries[0].id].max_health)
        self.assertEqual(storage.emissaries[emissaries[1].id].health,
                         storage.emissaries[emissaries[1].id].max_health - 1)
        self.assertEqual(storage.emissaries[emissaries[2].id].health,
                         storage.emissaries[emissaries[2].id].max_health - 1)


class KillDeadEmissariesTests(BaseEmissaryTests):

    def test(self):
        for i in range(3):
            self.create_emissary(clan=self.clan,
                                 initiator=self.account,
                                 place_id=random.choice(self.places).id)

        emissaries = list(storage.emissaries.all())

        self.assertEqual(len(emissaries), 3)

        emissaries[0].health = 0
        emissaries[2].health = -1

        logic.kill_dead_emissaries()

        self.assertNotIn(emissaries[0].id, storage.emissaries)
        self.assertTrue(storage.emissaries[emissaries[1].id].state.is_IN_GAME)
        self.assertNotIn(emissaries[2].id, storage.emissaries)

        self.assertTrue(logic.load_emissary(emissaries[0].id).state.is_OUT_GAME)
        self.assertTrue(logic.load_emissary(emissaries[2].id).state.is_OUT_GAME)


class MoveEmissaryTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        other_account = self.accounts_factory.create_account()
        other_clan = self.create_clan(owner=other_account, uid=2)

        self.emissaries = [self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=self.places[2].id),
                           self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=self.places[0].id),
                           self.create_emissary(clan=other_clan,
                                                initiator=other_account,
                                                place_id=self.places[2].id)]

    def test_move(self):

        game_turn.increment(delta=5)

        with self.check_changed(lambda: storage.emissaries.version):
            logic.move_emissary(initiator=self.account,
                                emissary_id=self.emissaries[1].id,
                                new_place_id=self.places[1].id)

        self.assertEqual(logic.load_emissary(emissary_id=self.emissaries[0].id).place_id, self.places[2].id)
        self.assertEqual(logic.load_emissary(emissary_id=self.emissaries[2].id).place_id, self.places[2].id)

        loaded_emissary = logic.load_emissary(emissary_id=self.emissaries[1].id)

        self.assertEqual(loaded_emissary.place_id, self.places[1].id)
        self.assertEqual(loaded_emissary.created_at_turn, self.emissaries[0].created_at_turn)
        self.assertEqual(loaded_emissary.updated_at_turn, game_turn.number())
        self.assertEqual(loaded_emissary.moved_at_turn, game_turn.number())

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_MOVED.meta_object().tag,
                          loaded_emissary.meta_object().tag,
                          self.account.meta_object().tag,
                          self.places[0].meta_object().tag,
                          self.places[1].meta_object().tag})

    def test_already_moved(self):
        game_turn.increment(delta=5)

        with self.check_not_changed(lambda: clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)):
            logic.move_emissary(initiator=self.account,
                                emissary_id=self.emissaries[1].id,
                                new_place_id=self.emissaries[1].place_id)

        loaded_emissary = logic.load_emissary(emissary_id=self.emissaries[1].id)

        self.assertEqual(loaded_emissary.place_id, self.places[0].id)
        self.assertEqual(loaded_emissary.created_at_turn, self.emissaries[0].created_at_turn)
        self.assertEqual(loaded_emissary.updated_at_turn, self.emissaries[0].updated_at_turn)
        self.assertEqual(loaded_emissary.moved_at_turn, self.emissaries[0].moved_at_turn)

    def test_already_removed(self):

        logic._remove_emissary(emissary_id=self.emissaries[1].id,
                               reason=relations.REMOVE_REASON.DISMISSED)

        game_turn.increment(delta=5)

        with self.check_not_changed(lambda: clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)):
            logic.move_emissary(initiator=self.account,
                                emissary_id=self.emissaries[1].id,
                                new_place_id=self.emissaries[1].place_id)

        loaded_emissary = logic.load_emissary(emissary_id=self.emissaries[1].id)

        self.assertEqual(loaded_emissary.place_id, self.places[0].id)
        self.assertEqual(loaded_emissary.created_at_turn, self.emissaries[0].created_at_turn)
        self.assertEqual(loaded_emissary.updated_at_turn, self.emissaries[0].updated_at_turn)
        self.assertEqual(loaded_emissary.moved_at_turn, self.emissaries[0].moved_at_turn)


class TTPowerImpactsTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=random.choice(self.places).id)

        self.actor_type = tt_api_impacts.OBJECT_TYPE.HERO
        self.actor_id = 666
        self.amount = 100500
        self.fame = 1000

        self.expected_power = round(self.emissary.place.attrs.freedom * self.amount)

    def test_place_inner_circle(self):
        impacts = list(logic.tt_power_impacts(place_inner_circle=True,
                                              can_change_place_power=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              emissary=self.emissary,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                            target_id=self.emissary.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=self.fame),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                            target_id=self.emissary.place.id,
                                                            amount=self.expected_power)])

    def test_can_not_change_place_power(self):
        impacts = list(logic.tt_power_impacts(place_inner_circle=True,
                                              can_change_place_power=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              emissary=self.emissary,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                            target_id=self.emissary.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=0),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=self.fame),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.JOB,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.JOB_PLACE_POSITIVE,
                                                            target_id=self.emissary.place.id,
                                                            amount=0)])

    def test_amount_below_zero(self):
        impacts = list(logic.tt_power_impacts(place_inner_circle=False,
                                              can_change_place_power=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              emissary=self.emissary,
                                              amount=-self.amount,
                                              fame=0))

        self.assertEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                            target_id=self.emissary.id,
                                                            amount=-self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=-self.expected_power)])

    def test_emissary_removed(self):
        self.emissary.state = relations.STATE.OUT_GAME

        impacts = list(logic.tt_power_impacts(place_inner_circle=False,
                                              can_change_place_power=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              emissary=self.emissary,
                                              amount=-self.amount,
                                              fame=0))

        self.assertEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=-self.expected_power)])


def fake_tt_power_impacts(**kwargs):
    yield kwargs


class ImpactsFromHeroTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=random.choice(self.places).id)

        self.amount = 100500
        self.fame = 1000

        self.expected_power = round(self.emissary.place.attrs.freedom * self.amount)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: False)
    def test_can_not_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        emissary=self.emissary,
                                                        power=1000,
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'emissary': self.emissary,
                                             'place_inner_circle': False,
                                             'can_change_place_power': False}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    @mock.patch('the_tale.game.heroes.objects.Hero.modify_politics_power', lambda self, power, emissary: power * 0.75)
    def test_can_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        emissary=self.emissary,
                                                        power=1000,
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 750,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'emissary': self.emissary,
                                             'place_inner_circle': False,
                                             'can_change_place_power': True}])
