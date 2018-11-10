
import smart_imports

smart_imports.all()


class GeneralTest(utils_testcase.TestCase):

    def setUp(self):
        super(GeneralTest, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

        self.bundle_id = self.action_idl.bundle_id

    def test_HELP_CHOICES(self):
        for action_class in list(prototypes.ACTION_TYPES.values()):
            self.assertTrue('HELP_CHOICES' in action_class.__dict__)
            if (not action_class.TYPE.is_IDLENESS and           # TODO: check
                not action_class.TYPE.is_BATTLE_PVE_1X1 and     # TODO: check
                not action_class.TYPE.is_MOVE_TO and            # TODO: check
                not action_class.TYPE.is_HEAL_COMPANION and
                    not action_class.TYPE.is_RESURRECT):
                self.assertIn(abilities_relations.HELP_CHOICES.MONEY, action_class.HELP_CHOICES)  # every action MUST has MONEY choice, or it will be great disbalance in energy & experience receiving

    def test_TEXTGEN_TYPE(self):
        for action_class in list(prototypes.ACTION_TYPES.values()):
            self.assertTrue('TEXTGEN_TYPE' in action_class.__dict__)

    def test_get_help_choice_has_heal(self):
        self.hero.health = 1

        heal_found = False
        for i in range(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == abilities_relations.HELP_CHOICES.HEAL)

        self.assertTrue(heal_found)

    def check_heal_in_choices(self, result):
        heal_found = False
        for i in range(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == abilities_relations.HELP_CHOICES.HEAL)

        self.assertEqual(heal_found, result)

    def check_heal_companion_in_choices(self, result):
        heal_found = False
        for i in range(100):
            heal_found = heal_found or (self.action_idl.get_help_choice() == abilities_relations.HELP_CHOICES.HEAL_COMPANION)

        self.assertEqual(heal_found, result)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_full_health_without_alternative(self):
        self.check_heal_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL, abilities_relations.HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_full_health_with_alternative(self):
        self.check_heal_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_large_health_without_alternative(self):
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL, abilities_relations.HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_large_health_with_alternative(self):
        self.hero.health = self.hero.max_health - 1
        self.check_heal_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL,)))
    def test_help_choice_has_heal__for_low_health_without_alternative(self):
        self.hero.health = 1
        self.check_heal_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL, abilities_relations.HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal__for_low_health_with_alternative(self):
        self.hero.health = 1
        self.check_heal_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL_COMPANION,)))
    def test_help_choice_has_heal_companion__for_no_companion(self):
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL_COMPANION, abilities_relations.HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal_companion__for_no_companion_with_alternative(self):
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL_COMPANION,)))
    def test_help_choice_has_heal_companion__for_full_health_without_alternative(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL_COMPANION,)))
    @mock.patch('the_tale.game.heroes.objects.Hero.companion_heal_disabled', lambda hero: True)
    def test_help_choice_has_heal_companion__for_companion_heal_disabled(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL_COMPANION, abilities_relations.HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal_companion__for_full_health_with_alternative(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.check_heal_companion_in_choices(False)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL_COMPANION,)))
    def test_help_choice_has_heal_companion__for_low_health_without_alternative(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.companion.health = 1
        self.check_heal_companion_in_choices(True)

    @mock.patch('the_tale.game.actions.prototypes.ActionIdlenessPrototype.HELP_CHOICES', set((abilities_relations.HELP_CHOICES.HEAL_COMPANION, abilities_relations.HELP_CHOICES.MONEY)))
    def test_help_choice_has_heal_companion__for_low_health_with_alternative(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        self.hero.set_companion(companions_logic.create_companion(companion_record))
        self.hero.companion.health = 1
        self.check_heal_companion_in_choices(True)

    def test_percents_consistency(self):
        # just test that quest will be ended
        while not self.action_idl.leader:
            self.storage.process_turn()
            game_turn.increment()
            self.assertEqual(self.storage.tests_get_last_action().percents, self.hero.last_action_percents)

    def test_help_choice_heal_not_in_choices_for_dead_hero(self):

        self.hero.health = 1
        heroes_logic.save_hero(self.hero)

        self.assertTrue(abilities_relations.HELP_CHOICES.HEAL in self.action_idl.help_choices)

        self.hero.kill()
        heroes_logic.save_hero(self.hero)

        self.assertFalse(abilities_relations.HELP_CHOICES.HEAL in self.action_idl.help_choices)

    def test_action_default_serialization(self):
        default_action = helpers.TestAction(hero=self.hero,
                                            bundle_id=self.bundle_id,
                                            state=helpers.TestAction.STATE.UNINITIALIZED)

        self.assertEqual(default_action.serialize(), {'bundle_id': self.bundle_id,
                                                      'state': helpers.TestAction.STATE.UNINITIALIZED,
                                                      'percents': 0.0,
                                                      'description': None,
                                                      'type': helpers.TestAction.TYPE.value,
                                                      'created_at_turn': game_turn.number()})
        deserialized_action = helpers.TestAction.deserialize(default_action.serialize())
        deserialized_action.hero = self.hero
        self.assertEqual(default_action, deserialized_action)

    def test_action_full_serialization(self):
        mob = mobs_storage.mobs.create_mob_for_hero(self.hero)

        account_2 = self.accounts_factory.create_account()

        self.storage.load_account_data(account_2)
        hero_2 = self.storage.accounts_to_heroes[account_2.id]

        meta_action = meta_actions.ArenaPvP1x1.create(self.storage, self.hero, hero_2)

        default_action = helpers.TestAction(hero=self.hero,
                                            bundle_id=self.bundle_id,
                                            state=helpers.TestAction.STATE.UNINITIALIZED,
                                            created_at_turn=666,
                                            context=helpers.TestAction.CONTEXT_MANAGER(),
                                            description='description',
                                            place_id=2,
                                            mob=mob,
                                            data={'xxx': 'yyy'},
                                            break_at=0.75,
                                            length=777,
                                            destination_x=20,
                                            destination_y=30,
                                            percents_barier=77,
                                            extra_probability=0.6,
                                            mob_context=helpers.TestAction.CONTEXT_MANAGER(),
                                            textgen_id='textgen_id',
                                            back=True,
                                            info_link='/bla-bla',
                                            meta_action=meta_action,
                                            replane_required=True)

        self.assertEqual(default_action.serialize(), {'bundle_id': self.bundle_id,
                                                      'state': helpers.TestAction.STATE.UNINITIALIZED,
                                                      'context': helpers.TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob_context': helpers.TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob': mob.serialize(),
                                                      'length': 777,
                                                      'back': True,
                                                      'textgen_id': 'textgen_id',
                                                      'extra_probability': 0.6,
                                                      'percents_barier': 77,
                                                      'destination_x': 20,
                                                      'destination_y': 30,
                                                      'percents': 0.0,
                                                      'description': 'description',
                                                      'type': helpers.TestAction.TYPE.value,
                                                      'created_at_turn': 666,
                                                      'place_id': 2,
                                                      'data': {'xxx': 'yyy'},
                                                      'info_link': '/bla-bla',
                                                      'break_at': 0.75,
                                                      'meta_action': meta_action.serialize(),
                                                      'replane_required': True})
        deserialized_action = helpers.TestAction.deserialize(default_action.serialize())
        deserialized_action.hero = self.hero
        self.assertEqual(default_action, deserialized_action)
