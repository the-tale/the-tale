
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
        self.assertEqual(emissary.place_rating_position, None)

        loaded_emissary = logic.load_emissary(emissary.id)

        self.assertEqual(emissary.attrs.serialize(), loaded_emissary.attrs.serialize())
        self.assertEqual(emissary, loaded_emissary)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_CREATED.meta_object().tag,
                          self.account.meta_object().tag,
                          emissary.meta_object().tag,
                          emissary.place.meta_object().tag})

        power = politic_power_logic.get_emissaries_power([emissary.id])[emissary.id]

        self.assertEqual(power, logic.expected_power_per_day())


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

    def test_stop_events(self):
        concrete_event = events.Rest(raw_ability_power=100500)

        test_events = []

        for emissary in self.emissaries:
            test_events.append(logic.create_event(initiator=self.account,
                                                  emissary=emissary,
                                                  concrete_event=concrete_event,
                                                  days=7))

        logic.finish_event(test_events[1])

        logic._remove_emissary(emissary_id=self.emissaries[2].id,
                               reason=relations.REMOVE_REASON.DISMISSED)

        self.assertTrue(logic.load_event(test_events[0].id).state.is_RUNNING)

        event = logic.load_event(test_events[1].id)
        self.assertTrue(event.state.is_STOPPED)
        self.assertTrue(event.stop_reason.is_FINISHED)

        event = logic.load_event(test_events[2].id)
        self.assertTrue(event.state.is_STOPPED)
        self.assertTrue(event.stop_reason.is_EMISSARY_LEFT_GAME)


class DismissEmissaryTests(BaseEmissaryTests):

    def test(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=random.choice(self.places).id)

        logic.dismiss_emissary(emissary_id=emissary.id)

        loaded_emissary = logic.load_emissary(emissary_id=emissary.id)

        self.assertTrue(loaded_emissary.state.is_OUT_GAME)
        self.assertTrue(loaded_emissary.remove_reason.is_DISMISSED)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_DISSMISSED.meta_object().tag,
                          emissary.meta_object().tag,
                          emissary.place.meta_object().tag})


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

        self.assertEqual(emissary.health, emissary.attrs.max_health)

        logic.damage_emissary(emissary_id=emissary.id)

        loaded_emissary = logic.load_emissary(emissary_id=emissary.id)

        self.assertEqual(loaded_emissary.health, loaded_emissary.attrs.max_health - loaded_emissary.attrs.damage_to_health)
        self.assertTrue(loaded_emissary.state.is_IN_GAME)

        self.assertEqual(emissary.health, emissary.attrs.max_health - emissary.attrs.damage_to_health)

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

        initial_power = logic.expected_power_per_day()

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
                                                                            amount=-initial_power),
                                                game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                            actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                            actor_id=666,
                                                                            target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                            target_id=emissaries[2].id,
                                                                            amount=-initial_power - 1000)])

        logic.damage_emissaries()

        self.assertEqual(storage.emissaries[emissaries[0].id].health,
                         storage.emissaries[emissaries[0].id].attrs.max_health)
        self.assertEqual(storage.emissaries[emissaries[1].id].health,
                         storage.emissaries[emissaries[1].id].attrs.max_health -
                         storage.emissaries[emissaries[1].id].attrs.damage_to_health)
        self.assertEqual(storage.emissaries[emissaries[2].id].health,
                         storage.emissaries[emissaries[2].id].attrs.max_health -
                         storage.emissaries[emissaries[2].id].attrs.damage_to_health)


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

        impact = game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                              actor_type=tt_api_impacts.OBJECT_TYPE.ACCOUNT,
                                              actor_id=accounts_logic.get_system_user_id(),
                                              target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                              target_id=self.emissaries[1].id,
                                              amount=logic.expected_power_per_day() + random.randint(1, 100500))

        politic_power_logic.add_power_impacts([impact])

        self.assertNotEqual(logic.expected_power_per_day(), self.get_emissary_power())

    def get_emissary_power(self):
        id = self.emissaries[1].id
        return politic_power_logic.get_emissaries_power(emissaries_ids=[id])[id]

    def test_move(self):

        game_turn.increment(delta=5)

        self.emissaries[1].place_rating_position = 666
        logic.save_emissary(self.emissaries[1])

        with self.check_changed(lambda: storage.emissaries.version):
            logic.move_emissary(emissary_id=self.emissaries[1].id,
                                new_place_id=self.places[1].id)

        self.assertEqual(self.emissaries[1].place_rating_position, None)

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
                          self.places[0].meta_object().tag,
                          self.places[1].meta_object().tag})

        self.assertEqual(logic.expected_power_per_day(), self.get_emissary_power())

    def test_already_moved(self):
        game_turn.increment(delta=5)

        with self.check_not_changed(self.get_emissary_power):
            with self.check_not_changed(lambda: clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)):
                logic.move_emissary(emissary_id=self.emissaries[1].id,
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
            logic.move_emissary(emissary_id=self.emissaries[1].id,
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

        self.emissary.attrs.positive_power = 1.0
        self.emissary.attrs.negative_power = 1.0

        self.actor_type = tt_api_impacts.OBJECT_TYPE.HERO
        self.actor_id = 666
        self.amount = 100500
        self.fame = 1000

        self.expected_power = self.emissary.place.attrs.freedom * self.amount

    def test_place_inner_circle(self):

        multiplier = 1.5

        self.emissary.attrs.positive_power = multiplier

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
                                                            amount=round(multiplier * self.expected_power)),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=round(multiplier * self.expected_power)),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=round(multiplier * self.expected_power)),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=self.fame)])

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
                                                            amount=round(self.expected_power)),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.emissary.place.id,
                                                            amount=0),
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
                                                            amount=self.fame)])

    def test_amount_below_zero(self):
        multiplier = 0.75

        self.emissary.attrs.negative_power = multiplier

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
                                                       amount=round(-multiplier * self.expected_power)),
                          game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                       actor_type=self.actor_type,
                                                       actor_id=self.actor_id,
                                                       target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                       target_id=self.emissary.place.id,
                                                       amount=round(-multiplier * self.expected_power))])

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
                                                       amount=round(-self.expected_power))])


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


class SyncPowerTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissaries = [self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id),
                           self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id)]

        game_tt_services.debug_clear_service()

    def test(self):
        impacts = []
        for power, emissary in zip((100, 300), self.emissaries):
            impacts.append(game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                        actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                        actor_id=self.account.id,
                                                        target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                        target_id=emissary.id,
                                                        amount=power))
        politic_power_logic.add_power_impacts(impacts)

        logic.sync_power()

        powers = politic_power_logic.get_emissaries_power(emissaries_ids=[emissary.id for emissary in self.emissaries])

        self.assertEqual(powers, {self.emissaries[0].id: 99,
                                  self.emissaries[1].id: 297})


class GenerateTraitsTests(BaseEmissaryTests):

    def test(self):
        for i in range(1000):
            traits = logic.generate_traits()

            types = collections.Counter(trait.type for trait in traits)

            self.assertEqual(types, {relations.TRAIT_TYPE.POSITIVE: tt_emissaries_constants.POSITIVE_TRAITS_NUMBER,
                                     relations.TRAIT_TYPE.NEGATIVE: tt_emissaries_constants.NEGATIVE_TRAITS_NUMBER})

            attributes = {trait.attribute for trait in traits}

            self.assertEqual(len(attributes),
                             tt_emissaries_constants.POSITIVE_TRAITS_NUMBER + tt_emissaries_constants.NEGATIVE_TRAITS_NUMBER)


class CreateEventTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=random.choice(self.places).id)

        game_tt_services.debug_clear_service()

    def test(self):

        concrete_event = events.Rest(raw_ability_power=100500)

        days = 7

        event = logic.create_event(initiator=self.account,
                                   emissary=self.emissary,
                                   concrete_event=concrete_event,
                                   days=days)

        self.assertEqual(event.emissary_id, self.emissary.id)
        self.assertEqual(event.concrete_event, concrete_event)
        self.assertEqual(event.steps_processed, 0)
        self.assertEqual(event.stop_after_steps, 24 * days)
        self.assertTrue(event.state.is_RUNNING)
        self.assertTrue(event.stop_reason.is_NOT_STOPPED)

        loaded_event = logic.load_event(event.id)

        self.assertEqual(event, loaded_event)

        total_events, clan_events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(clan_events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_EVENT_CREATED.meta_object().tag,
                          self.account.meta_object().tag,
                          self.emissary.meta_object().tag,
                          self.emissary.place.meta_object().tag,
                          concrete_event.TYPE.meta_object().tag})


class LoadEventsTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissaries = [self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id),
                           self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id),
                           self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id),
                           self.create_emissary(clan=self.clan,
                                                initiator=self.account,
                                                place_id=random.choice(self.places).id)]

        concrete_event = events.Rest(raw_ability_power=100500)

        self.created_events = []

        for emissary in (self.emissaries[0],
                         self.emissaries[0],
                         self.emissaries[1],
                         self.emissaries[2],
                         self.emissaries[2],
                         self.emissaries[3]):

            self.created_events.append(logic.create_event(initiator=self.account,
                                                          emissary=emissary,
                                                          concrete_event=concrete_event,
                                                          days=7))

        logic.cancel_event(self.account, self.created_events[3])


class StopEventTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=random.choice(self.places).id)

        concrete_event = events.Rest(raw_ability_power=100500)

        self.event = logic.create_event(initiator=self.account,
                                        emissary=self.emissary,
                                        concrete_event=concrete_event,
                                        days=7)

    def test_stop_event(self):
        reason = relations.EVENT_STOP_REASON.random(exclude=(relations.EVENT_STOP_REASON.NOT_STOPPED,))

        logic._stop_event(self.event, reason)

        self.assertTrue(self.event.state.is_STOPPED)
        self.assertEqual(self.event.stop_reason, reason)

        loaded_event = logic.load_event(self.event.id)

        self.event.updated_at = loaded_event.updated_at

        self.assertEqual(self.event, loaded_event)

    def test_cancel_event(self):

        with mock.patch('the_tale.game.emissaries.events.EventBase.on_cancel') as on_cancel:
            logic.cancel_event(self.account, self.event)

        self.assertTrue(on_cancel.called)

        loaded_event = logic.load_event(self.event.id)

        self.assertTrue(loaded_event.state.is_STOPPED)
        self.assertTrue(loaded_event.stop_reason.is_STOPPED_BY_PLAYER)

        total_events, clan_events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(clan_events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_EVENT_CANCELED.meta_object().tag,
                          self.account.meta_object().tag,
                          self.emissary.meta_object().tag,
                          self.emissary.place.meta_object().tag,
                          self.event.concrete_event.TYPE.meta_object().tag})

    def test_finish_event(self):
        with mock.patch('the_tale.game.emissaries.events.EventBase.on_cancel') as on_cancel:
            logic.finish_event(self.event)

        on_cancel.assert_not_called()

        loaded_event = logic.load_event(self.event.id)

        self.assertTrue(loaded_event.state.is_STOPPED)
        self.assertTrue(loaded_event.stop_reason.is_FINISHED)

        total_events, clan_events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(clan_events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_EVENT_FINISHED.meta_object().tag,
                          self.emissary.meta_object().tag,
                          self.emissary.place.meta_object().tag,
                          self.event.concrete_event.TYPE.meta_object().tag})

    def test_stop_event_due_emissary_left_game(self):
        with mock.patch('the_tale.game.emissaries.events.EventBase.on_cancel') as on_cancel:
            logic.stop_event_due_emissary_left_game(self.event)

        self.assertTrue(on_cancel.called)

        loaded_event = logic.load_event(self.event.id)

        self.assertTrue(loaded_event.state.is_STOPPED)
        self.assertTrue(loaded_event.stop_reason.is_EMISSARY_LEFT_GAME)

        total_events, clan_events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(clan_events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_EVENT_FINISHED.meta_object().tag,
                          self.emissary.meta_object().tag,
                          self.emissary.place.meta_object().tag,
                          self.event.concrete_event.TYPE.meta_object().tag})


class DoEventStepTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=random.choice(self.places).id)

        self.emissary.health = 1

        logic.save_emissary(self.emissary)

        concrete_event = events.Rest(raw_ability_power=100500)

        self.event = logic.create_event(initiator=self.account,
                                        emissary=self.emissary,
                                        concrete_event=concrete_event,
                                        days=7)

    def test_event_not_running(self):
        logic.finish_event(self.event)

        with self.check_not_changed(lambda: logic.load_emissary(self.emissary.id).health):
            with self.check_not_changed(lambda: logic.load_event(self.event.id).steps_processed):
                self.assertTrue(logic.do_event_step(self.event.id))

    def test_step(self):
        self.event.created_at = datetime.datetime.now() - datetime.timedelta(hours=2)
        models.Event.objects.filter(id=self.event.id).update(created_at=self.event.created_at)

        with self.check_increased(lambda: logic.load_emissary(self.emissary.id).health):
            with self.check_delta(lambda: logic.load_event(self.event.id).steps_processed, 1):
                self.assertTrue(logic.do_event_step(self.event.id))

        self.assertTrue(logic.load_event(self.event.id).state.is_RUNNING)

    def test_step_with_error(self):
        self.event.created_at = datetime.datetime.now() - datetime.timedelta(hours=2)
        models.Event.objects.filter(id=self.event.id).update(created_at=self.event.created_at)

        with mock.patch('the_tale.game.emissaries.events.Rest.on_step', mock.Mock(return_value=False)):
            with self.check_not_changed(lambda: logic.load_emissary(self.emissary.id).health):
                with self.check_not_changed(lambda: logic.load_event(self.event.id).steps_processed):
                    self.assertFalse(logic.do_event_step(self.event.id))

        self.assertTrue(logic.load_event(self.event.id).state.is_RUNNING)

    def test_finish(self):
        self.event.steps_processed = self.event.stop_after_steps - 1

        logic.save_event(self.event)

        with self.check_increased(lambda: logic.load_emissary(self.emissary.id).health):
            with self.check_increased(lambda: logic.load_event(self.event.id).steps_processed):
                self.assertTrue(logic.do_event_step(self.event.id))

        self.assertTrue(logic.load_event(self.event.id).state.is_STOPPED)

    def test_finish__on_finish(self):

        event = logic.create_event(initiator=self.account,
                                   emissary=self.emissary,
                                   concrete_event=events.Dismiss(raw_ability_power=100500),
                                   days=1)

        event.steps_processed = event.stop_after_steps - 1

        logic.save_event(event)
        self.assertTrue(logic.do_event_step(event.id))

        self.assertTrue(logic.load_event(event.id).state.is_STOPPED)
        self.assertTrue(logic.load_emissary(event.emissary_id).state.is_OUT_GAME)


class AddClanExperienceTests(utils_testcase.TestCase,
                             clans_helpers.ClansTestsMixin,
                             helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        clans_tt_services.chronicle.cmd_debug_clear_service()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

    def _create_event(self, emissary):
        concrete_event = events.Rest(raw_ability_power=100500)

        initiator = None

        for account in self.accounts:
            if account.clan_id == emissary.clan_id:
                initiator = account
                break

        return logic.create_event(initiator=initiator,
                                  emissary=emissary,
                                  concrete_event=concrete_event,
                                  days=7)

    def _create_emissary(self, i):
        return self.create_emissary(clan=self.clans[i],
                                    initiator=self.accounts[i],
                                    place_id=random.choice(self.places).id)

    def get_experience(self, clan_id):
        return clans_tt_services.currencies.cmd_balance(clan_id, currency=clans_relations.CURRENCY.EXPERIENCE)

    def test(self):
        # clan 0 — no events
        # clan 1 — single event
        # clan 2 — multiple events single emissary
        # clan 3 — multiple events multiple emissary
        # clan 4 - only finished events

        self.accounts = [self.accounts_factory.create_account() for i in range(5)]
        self.clans = [self.create_clan(owner=account, uid=i) for i, account in enumerate(self.accounts)]

        emissary_1_1 = self._create_emissary(1)

        self._create_event(emissary_1_1)

        emissary_2_1 = self._create_emissary(2)
        self._create_event(emissary_2_1)
        self._create_event(emissary_2_1)

        emissary_3_1 = self._create_emissary(3)
        emissary_3_2 = self._create_emissary(3)

        self._create_event(emissary_3_1)
        self._create_event(emissary_3_2)
        self._create_event(emissary_3_2)

        emissary_4_1 = self._create_emissary(4)

        for emissary in [emissary_1_1,
                         emissary_2_1,
                         emissary_3_1,
                         emissary_3_2,
                         emissary_4_1]:
            emissary.traits = frozenset()
            emissary.refresh_attributes()
            logic.save_emissary(emissary)

        logic.finish_event(self._create_event(emissary_4_1))

        with self.check_not_changed(lambda: self.get_experience(self.clans[0].id)):
            with self.check_delta(lambda: self.get_experience(self.clans[1].id),
                                  tt_clans_constants.EXPERIENCE_PER_EVENT):
                with self.check_delta(lambda: self.get_experience(self.clans[2].id),
                                      2 * tt_clans_constants.EXPERIENCE_PER_EVENT):
                    with self.check_delta(lambda: self.get_experience(self.clans[3].id),
                                          3 * tt_clans_constants.EXPERIENCE_PER_EVENT):
                        with self.check_not_changed(lambda: self.get_experience(self.clans[4].id)):
                            logic.add_clan_experience()

    def test_experience_modifier(self):
        account = self.accounts_factory.create_account()
        clan = self.create_clan(owner=account, uid=1)

        emissary = self.create_emissary(clan=clan,
                                        initiator=account,
                                        place_id=random.choice(self.places).id)

        multiplier = 1.5

        emissary.attrs.clan_experience = multiplier

        concrete_event = events.Rest(raw_ability_power=100500)

        logic.create_event(initiator=account,
                           emissary=emissary,
                           concrete_event=concrete_event,
                           days=7)

        with self.check_delta(lambda: self.get_experience(clan.id),
                              multiplier * tt_clans_constants.EXPERIENCE_PER_EVENT):
            logic.add_clan_experience()


class AddEmissariesExperienceTests(utils_testcase.TestCase,
                                   clans_helpers.ClansTestsMixin,
                                   helpers.EmissariesTestsMixin):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        clans_tt_services.chronicle.cmd_debug_clear_service()

        self.forum_category = forum_prototypes.CategoryPrototype.create(caption='category-1',
                                                                        slug=clans_conf.settings.FORUM_CATEGORY_SLUG,
                                                                        order=0)

        self.concrete_event = events.Rest(raw_ability_power=100500)

    def _create_event(self, emissary):

        initiator = None

        for account in self.accounts:
            if account.clan_id == emissary.clan_id:
                initiator = account
                break

        return logic.create_event(initiator=initiator,
                                  emissary=emissary,
                                  concrete_event=self.concrete_event,
                                  days=7)

    def _create_emissary(self, i):
        emissary = self.create_emissary(clan=self.clans[i],
                                        initiator=self.accounts[i],
                                        place_id=random.choice(self.places).id)
        emissary.traits = frozenset()

        emissary.refresh_attributes()

        logic.save_emissary(emissary)

        return emissary

    def check_emissary_abilities(self, emissary, expected_abilities):
        abilities = {ability: 0 for ability in relations.ABILITY.records}
        abilities.update(expected_abilities)

        self.assertEqual(dict(emissary.abilities.items()), abilities)
        self.assertEqual(dict(logic.load_emissary(emissary.id).abilities.items()), abilities)

    def test(self):
        # clan 0 — no events
        # clan 1 — single event
        # clan 2 — multiple events single emissary
        # clan 3 — multiple events multiple emissary
        # clan 4 - only finished events

        self.accounts = [self.accounts_factory.create_account() for i in range(5)]
        self.clans = [self.create_clan(owner=account, uid=i) for i, account in enumerate(self.accounts)]

        emissary_1_1 = self._create_emissary(1)

        self._create_event(emissary_1_1)

        emissary_2_1 = self._create_emissary(2)
        self._create_event(emissary_2_1)
        self._create_event(emissary_2_1)

        emissary_3_1 = self._create_emissary(3)
        emissary_3_2 = self._create_emissary(3)

        self._create_event(emissary_3_1)
        self._create_event(emissary_3_2)
        self._create_event(emissary_3_2)

        emissary_4_1 = self._create_emissary(4)

        for emissary in [emissary_1_1,
                         emissary_2_1,
                         emissary_3_1,
                         emissary_3_2,
                         emissary_4_1]:
            emissary.traits = frozenset()
            emissary.refresh_attributes()
            logic.save_emissary(emissary)

        logic.finish_event(self._create_event(emissary_4_1))

        logic.add_emissaries_experience()

        self.check_emissary_abilities(emissary_1_1, {ability: tt_emissaries_constants.ATTRIBUT_INCREMENT_DELTA
                                                     for ability in self.concrete_event.TYPE.abilities})
        self.check_emissary_abilities(emissary_2_1, {ability: 2 * tt_emissaries_constants.ATTRIBUT_INCREMENT_DELTA
                                                     for ability in self.concrete_event.TYPE.abilities})
        self.check_emissary_abilities(emissary_3_1, {ability: tt_emissaries_constants.ATTRIBUT_INCREMENT_DELTA
                                                     for ability in self.concrete_event.TYPE.abilities})
        self.check_emissary_abilities(emissary_3_2, {ability: 2 * tt_emissaries_constants.ATTRIBUT_INCREMENT_DELTA
                                                     for ability in self.concrete_event.TYPE.abilities})
        self.check_emissary_abilities(emissary_4_1, {})


class ExpectedPowerPerDayTests(BaseEmissaryTests):

    def test(self):
        # на текущий момент значение зависит от количества и рассположения городов
        # поэтому в тестах оно меньше
        self.assertEqual(logic.expected_power_per_day(), 17)


class RenameEmissaryTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=self.places[2].id)

    def test_rename(self):

        new_name = game_names.generator().get_test_name()

        self.assertNotEqual(self.emissary.utg_name, new_name)

        with self.check_changed(lambda: storage.emissaries.version):
            logic.rename_emissary(emissary_id=self.emissary.id,
                                  new_name=new_name)

        self.assertEqual(self.emissary.utg_name, new_name)
        self.assertEqual(logic.load_emissary(emissary_id=self.emissary.id).utg_name, new_name)

        total_events, events = clans_tt_services.chronicle.cmd_get_last_events(self.clan, tags=(), number=1000)

        self.assertEqual(set(events[0].tags),
                         {self.clan.meta_object().tag,
                          clans_relations.EVENT.EMISSARY_RENAMED.meta_object().tag,
                          self.places[2].meta_object().tag,
                          self.emissary.meta_object().tag})


class UpdateEmissariesRating(BaseEmissaryTests):
    def setUp(self):
        super().setUp()

        self.emissaries_0_ids = [self.create_emissary(clan=self.clan,
                                                      initiator=self.account,
                                                      place_id=self.places[0].id).id
                                                      for i in range(10)]

        self.emissaries_1_ids = [self.create_emissary(clan=self.clan,
                                                      initiator=self.account,
                                                      place_id=self.places[1].id).id
                                                      for i in range(3)]

    def add_power(self, powers):
        impacts = []

        for emissary_id, power in powers.items():
            impacts.append(game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                        actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                        actor_id=666,
                                                        target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                        target_id=emissary_id,
                                                        amount=power))
        politic_power_logic.add_power_impacts(impacts)

    def test(self):
        self.add_power(powers={self.emissaries_0_ids[0]: -2000,
                               self.emissaries_0_ids[1]: 1000,
                               self.emissaries_0_ids[3]: -1000,
                               self.emissaries_0_ids[5]: 3000,
                               self.emissaries_0_ids[6]: 2000,
                               self.emissaries_0_ids[7]: 2500,

                               self.emissaries_1_ids[0]: -1000,
                               self.emissaries_1_ids[1]: 5000,
                               self.emissaries_1_ids[2]: 2000})

        logic.update_emissaries_ratings()

        storage.emissaries.refresh()

        expected_rating_positions_0 = [9, 3, 4, 8, 5, 0, 2, 1, 6, 7]
        expected_rating_positions_1 = [2, 0, 1]

        for emissary_id, expected_rating_position in zip(self.emissaries_0_ids, expected_rating_positions_0):
            self.assertEqual(storage.emissaries[emissary_id].place_rating_position, expected_rating_position)

        for emissary_id, expected_rating_position in zip(self.emissaries_1_ids, expected_rating_positions_1):
            self.assertEqual(storage.emissaries[emissary_id].place_rating_position, expected_rating_position)


class WithdrawEventPointsTests(BaseEmissaryTests):
    CURRENCY = relations.EVENT_CURRENCY.random()

    def get_event_points(self):
        return tt_services.events_currencies.cmd_balance(logic.resource_id(self.clan.id, self.places[0].id),
                                                         currency=self.CURRENCY)

    def test_withdraw(self):
        with self.check_delta(self.get_event_points, -tt_emissaries_constants.EVENT_CURRENCY_MULTIPLIER):
            logic.withdraw_event_points(clan_id=self.clan.id,
                                        place_id=self.places[0].id,
                                        currency=self.CURRENCY)


class CanClanParticipateInPvpTests(BaseEmissaryTests):

    def test__no_emissaries(self):
        self.assertFalse(logic.can_clan_participate_in_pvp(self.clan.id))

    def test_no_abilities(self):
        self.create_emissary(clan=self.clan,
                             initiator=self.account,
                             place_id=self.places[0].id)

        self.assertFalse(logic.can_clan_participate_in_pvp(self.clan.id))

    def test_has_abilities(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=self.places[0].id)

        def can_participate_in_pvp(self):
            return self.id == emissary.id

        self.create_emissary(clan=self.clan,
                             initiator=self.account,
                             place_id=self.places[0].id)

        with mock.patch('the_tale.game.emissaries.objects.Emissary.can_participate_in_pvp', can_participate_in_pvp):
            self.assertTrue(logic.can_clan_participate_in_pvp(self.clan.id))


class SendEventSuccessMessageTests(BaseEmissaryTests):

    def setUp(self):
        super().setUp()

        personal_messages_tt_services.personal_messages.cmd_debug_clear_service()

    def test_single_emissary(self):

        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=self.places[0].id)

        concrete_event = events.Rest(raw_ability_power=666)

        emissary_event = logic.create_event(initiator=self.account,
                                            emissary=emissary,
                                            concrete_event=concrete_event,
                                            days=7)

        logic.send_event_success_message(emissary_event,
                                         account=self.account,
                                         suffix='xxx')

        messages_count, messages = personal_messages_tt_services.personal_messages.cmd_get_received_messages(account_id=self.account.id)

        self.assertIn(emissary.utg_name.forms[1], messages[0].body)
        self.assertIn('xxx', messages[0].body)

    def test_multiple_emissaries(self):

        emissaries = [self.create_emissary(clan=self.clan,
                                           initiator=self.account,
                                           place_id=self.places[0].id),
                      self.create_emissary(clan=self.clan,
                                           initiator=self.account,
                                           place_id=self.places[1].id)]

        concrete_event = events.Rest(raw_ability_power=666)

        emissary_events = [logic.create_event(initiator=self.account,
                                              emissary=emissaries[0],
                                              concrete_event=concrete_event,
                                              days=7),
                           logic.create_event(initiator=self.account,
                                              emissary=emissaries[1],
                                              concrete_event=concrete_event,
                                              days=7)]

        logic.send_event_success_message(random.choice(emissary_events),
                                         account=self.account,
                                         suffix='xxx')

        messages_count, messages = personal_messages_tt_services.personal_messages.cmd_get_received_messages(account_id=self.account.id)

        self.assertTrue(all(emissaries[0].utg_name.forms[1] in messages[0].body for emissary in emissaries))
        self.assertTrue(all('xxx' in messages[0].body for emissary in emissaries))


class ProcessEventsMonitoring(BaseEmissaryTests):

    def test_save_event_on_change(self):
        emissary = self.create_emissary(clan=self.clan,
                                        initiator=self.account,
                                        place_id=self.places[0].id)

        emissary_events = [logic.create_event(initiator=self.account,
                                              emissary=emissary,
                                              concrete_event=events.Rest(raw_ability_power=666),
                                              days=7),
                           logic.create_event(initiator=self.account,
                                              emissary=emissary,
                                              concrete_event=events.Dismiss(raw_ability_power=666),
                                              days=7)]

        updated_at = [event.updated_at for event in emissary_events]

        with mock.patch('the_tale.game.emissaries.events.Rest.on_monitoring', mock.Mock(return_value=True)):
            with mock.patch('the_tale.game.emissaries.events.Dismiss.on_monitoring', mock.Mock(return_value=False)):
                logic.process_events_monitoring()

        self.assertLess(updated_at[0], storage.events[emissary_events[0].id].updated_at)
        self.assertEqual(updated_at[1], storage.events[emissary_events[1].id].updated_at)
