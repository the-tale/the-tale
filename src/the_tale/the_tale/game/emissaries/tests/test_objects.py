
import smart_imports

smart_imports.all()


class EmissaryObjectTests(clans_helpers.ClansTestsMixin,
                          places_helpers.PlacesTestsMixin,
                          helpers.EmissariesTestsMixin,
                          utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=self.places[0].id)

        places_tt_services.effects.cmd_debug_clear_service()

    def test_can_participate_in_pvp(self):
        self.assertFalse(self.emissary.can_participate_in_pvp())

        lower = (tt_emissaries_constants.ATTRIBUTES_FOR_PARTICIPATE_IN_PVP - 1) // len(relations.ABILITY.records)

        for ability in relations.ABILITY.records:
            self.emissary.abilities[ability] = lower

        self.assertFalse(self.emissary.can_participate_in_pvp())

        self.enable_emissary_pvp(self.emissary)

        self.assertTrue(self.emissary.can_participate_in_pvp())

    def test_is_place_leader__no_position(self):
        self.emissary.place_rating_position = None

        self.assertFalse(self.emissary.is_place_leader())

    def test_is_place_leader__not_leader(self):
        self.emissary.place_rating_position = tt_emissaries_constants.PLACE_LEADERS_NUMBER

        self.assertFalse(self.emissary.is_place_leader())

    def test_is_place_leader__leader(self):
        self.emissary.place_rating_position = tt_emissaries_constants.PLACE_LEADERS_NUMBER - 1

        self.assertTrue(self.emissary.is_place_leader())

    def test_is_place_leader__out_game_leader(self):
        self.emissary.place_rating_position = tt_emissaries_constants.PLACE_LEADERS_NUMBER - 1
        self.emissary.state = relations.STATE.OUT_GAME

        self.assertFalse(self.emissary.is_place_leader())

    def test_protectorat_bonus(self):

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[0])

        self.set_protector(self.places[0].id, self.clan.id)

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[1])

        self.set_protector(self.places[1].id, self.clan.id)

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[2])

        self.set_protector(self.places[1].id, None)

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[1])

    def test_protectorat_bonus__wrong_protector(self):

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[0])

        self.set_protector(self.places[1].id, self.clan.id)

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[0])

        self.set_protector(self.places[0].id, self.clan.id + 1)

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[0])

        self.set_protector(self.places[0].id, self.clan.id)

        self.assertEqual(self.emissary.protectorat_event_bonus(), tt_emissaries_constants.PROTECTORAT_BONUSES[2])


class EventObjectTests(clans_helpers.ClansTestsMixin,
                       places_helpers.PlacesTestsMixin,
                       helpers.EmissariesTestsMixin,
                       utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

        self.emissary = self.create_emissary(clan=self.clan,
                                             initiator=self.account,
                                             place_id=self.places[0].id)

        self.event = logic.create_event(initiator=self.account,
                                        emissary=self.emissary,
                                        concrete_event=events.Rest(raw_ability_power=666),
                                        days=7)

    def test_stop_after(self):
        self.assertEqual(self.event.stop_after,
                         self.event.created_at + datetime.timedelta(days=7))

        total_steps = 24 * 7

        self.event.steps_processed += 23

        self.assertEqual(self.event.stop_after,
                         self.event.created_at + datetime.timedelta(hours=total_steps - 23))

        self.event.created_at += datetime.timedelta(hours=-5)

        self.assertEqual(self.event.stop_after,
                         self.event.created_at + datetime.timedelta(hours=total_steps - 23 + 5))
