
import smart_imports

smart_imports.all()


class GeneralTest(utils_testcase.TestCase):

    def setUp(self):
        super(GeneralTest, self).setUp()
        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

        self.bundle_id = self.action_idl.bundle_id

    def test_TEXTGEN_TYPE(self):
        for action_class in list(prototypes.ACTION_TYPES.values()):
            self.assertTrue('TEXTGEN_TYPE' in action_class.__dict__)

    def test_percents_consistency(self):
        # just test that quest will be ended
        while not self.action_idl.leader:
            self.storage.process_turn()
            game_turn.increment()
            self.assertEqual(self.storage.tests_get_last_action().percents, self.hero.last_action_percents)

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

        self.storage.load_account_data(account_2.id)
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
                                            percents_barier=77,
                                            extra_probability=0.6,
                                            mob_context=helpers.TestAction.CONTEXT_MANAGER(),
                                            textgen_id='textgen_id',
                                            info_link='/bla-bla',
                                            meta_action=meta_action,
                                            replane_required=True,
                                            path=navigation_path.Path(cells=[(1, 2)]))

        self.assertEqual(default_action.serialize(), {'bundle_id': self.bundle_id,
                                                      'state': helpers.TestAction.STATE.UNINITIALIZED,
                                                      'context': helpers.TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob_context': helpers.TestAction.CONTEXT_MANAGER().serialize(),
                                                      'mob': mob.serialize(),
                                                      'textgen_id': 'textgen_id',
                                                      'extra_probability': 0.6,
                                                      'percents_barier': 77,
                                                      'percents': 0.0,
                                                      'description': 'description',
                                                      'type': helpers.TestAction.TYPE.value,
                                                      'created_at_turn': 666,
                                                      'place_id': 2,
                                                      'data': {'xxx': 'yyy'},
                                                      'info_link': '/bla-bla',
                                                      'break_at': 0.75,
                                                      'meta_action': meta_action.serialize(),
                                                      'replane_required': True,
                                                      'path': navigation_path.Path(cells=[(1, 2)]).serialize()})
        deserialized_action = helpers.TestAction.deserialize(default_action.serialize())
        deserialized_action.hero = self.hero
        self.assertEqual(default_action, deserialized_action)
