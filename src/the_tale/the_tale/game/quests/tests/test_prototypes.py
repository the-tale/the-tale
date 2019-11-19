
import smart_imports

smart_imports.all()


TEST_FREEDOM = float(666)


class PrototypeTestsBase(utils_testcase.TestCase):

    def setUp(self):
        super(PrototypeTestsBase, self).setUp()
        game_turn.increment()

        game_tt_services.debug_clear_service()

        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account(is_fast=True)

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.action_idl = self.hero.actions.current_action

        self.action_idl.state = self.action_idl.STATE.QUEST

        self.action_quest = actions_prototypes.ActionQuestPrototype.create(hero=self.hero)
        helpers.setup_quest(self.hero)

        self.quest = self.hero.quests.current_quest


class PrototypeTests(PrototypeTestsBase,
                     clans_helpers.ClansTestsMixin,
                     emissaries_helpers.EmissariesTestsMixin):

    def setUp(self):
        super(PrototypeTests, self).setUp()

    def test_serialization(self):
        self.assertEqual(self.quest.serialize(), prototypes.QuestPrototype.deserialize(self.quest.serialize()).serialize())

    def test_do_step(self):
        with mock.patch('the_tale.game.quests.container.QuestsContainer.mark_updated') as mark_updated:
            self.quest.process()

        self.assertEqual(mark_updated.call_count, 1)

    def complete_quest(self, callback=lambda: None, positive_results=True):

        # save link to quest, since it will be removed from hero when quest finished
        quest = self.hero.quests.current_quest

        # modify quest results, to give only positive power
        if positive_results:
            for finish in quest.knowledge_base.filter(questgen_facts.Finish):
                finish.results = {object_uid: questgen_quests_base_quest.RESULTS.SUCCESSED for object_uid in finish.results.keys()}

        old_quests_done = self.hero.statistics.quests_done

        while not self.action_idl.leader:
            self.hero.health = self.hero.max_health
            self.storage.process_turn()
            callback()
            game_turn.increment()

        self.assertTrue(isinstance(quest.knowledge_base[quest.machine.pointer.state], questgen_facts.Finish))

        self.assertTrue(all(requirement.check(quest) for requirement in quest.knowledge_base[quest.machine.pointer.state].require))

        self.assertTrue(self.hero.quests.history[next(quest.knowledge_base.filter(questgen_facts.Start)).type] > 0)

        self.assertTrue(old_quests_done < self.hero.statistics.quests_done)

    def check_ui_info(self):
        s11n.to_json(self.hero.ui_info(actual_guaranteed=True))

    def test_complete_quest(self):
        self.assertEqual(self.hero.quests.interfered_persons, {})
        self.complete_quest(self.check_ui_info, positive_results=False)
        self.assertNotEqual(self.hero.quests.interfered_persons, {})

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_person_power', lambda self, person: True)
    def test_give_person_power__profession(self):

        person = persons_storage.persons.all()[0]

        power_without_profession = self.quest.finish_quest_person_power(questgen_quests_base_quest.RESULTS.SUCCESSED, uids.person(person.id))

        self.quest.knowledge_base += questgen_facts.ProfessionMarker(person=uids.person(person.id), profession=666)

        power_with_profession = self.quest.finish_quest_person_power(questgen_quests_base_quest.RESULTS.SUCCESSED, uids.person(person.id))

        self.assertTrue(power_with_profession < power_without_profession)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_person_power', lambda self, person: True)
    def test_give_person_power__profession_not_affect_power_bonus(self):

        person = persons_storage.persons.all()[0]

        self.quest.knowledge_base += questgen_facts.ProfessionMarker(person=uids.person(person.id), profession=666)

        power_with_profession = self.quest.finish_quest_person_power(questgen_quests_base_quest.RESULTS.SUCCESSED, uids.person(person.id))

        self.quest.current_info.power_bonus = 666

        new_power = self.quest.finish_quest_person_power(questgen_quests_base_quest.RESULTS.SUCCESSED, uids.person(person.id))

        self.assertEqual(power_with_profession + 666, new_power)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_person_power', lambda self, person: True)
    def test_give_person_power__power_bonus(self):
        person = persons_storage.persons.all()[0]

        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        power = self.quest.finish_quest_person_power(questgen_quests_base_quest.RESULTS.SUCCESSED, uids.person(person.id))
        self.assertEqual(power, 10 + 1)

        power = self.quest.finish_quest_person_power(questgen_quests_base_quest.RESULTS.FAILED, uids.person(person.id))
        self.assertEqual(power, -10 - 1)

        power = self.quest.finish_quest_person_power(questgen_quests_base_quest.RESULTS.NEUTRAL, uids.person(person.id))
        self.assertEqual(power, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_give_place_power__power_bonus(self):
        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        power = self.quest.finish_quest_place_power(questgen_quests_base_quest.RESULTS.SUCCESSED, uids.place(self.place_1.id))
        self.assertEqual(power, 10 + 1)

        power = self.quest.finish_quest_place_power(questgen_quests_base_quest.RESULTS.FAILED, uids.place(self.place_1.id))
        self.assertEqual(power, -10 - 1)

        power = self.quest.finish_quest_place_power(questgen_quests_base_quest.RESULTS.NEUTRAL, uids.place(self.place_1.id))
        self.assertEqual(power, 0)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, person: True)
    def test_give_emissary_power__power_bonus(self):
        self.prepair_forum_for_clans()

        account = self.accounts_factory.create_account()

        clan = self.create_clan(owner=account, uid=1)

        emissary = self.create_emissary(clan=clan,
                                        initiator=account,
                                        place_id=self.place_1.id)

        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        power = self.quest.finish_quest_emissary_power(questgen_quests_base_quest.RESULTS.SUCCESSED, uids.emissary(emissary.id))
        self.assertEqual(power, 10 + 1)

        power = self.quest.finish_quest_emissary_power(questgen_quests_base_quest.RESULTS.FAILED, uids.emissary(emissary.id))
        self.assertEqual(power, -10 - 1)

        power = self.quest.finish_quest_emissary_power(questgen_quests_base_quest.RESULTS.NEUTRAL, uids.emissary(emissary.id))
        self.assertEqual(power, 0)

    def test_power_on_end_quest_for_fast_account_hero(self):
        game_tt_services.debug_clear_service()

        self.assertEqual(places_logic.get_hero_popularity(self.hero.id).places_rating(), [])

        self.complete_quest()

        self.assertTrue(len(places_logic.get_hero_popularity(self.hero.id).places_rating()) > 0)

        impacts = politic_power_logic.get_last_power_impacts(limit=100)

        self.assertTrue(len(impacts) == 0)

    def test_power_on_end_quest_for_premium_account_hero(self):

        game_tt_services.debug_clear_service()

        self.hero.is_fast = False
        self.hero.premium_state_end_at = datetime.datetime.now() + datetime.timedelta(seconds=60)

        self.assertEqual(places_logic.get_hero_popularity(self.hero.id).places_rating(), [])

        self.complete_quest()

        self.assertTrue(len(places_logic.get_hero_popularity(self.hero.id).places_rating()) > 0)

        impacts = politic_power_logic.get_last_power_impacts(limit=100)

        self.assertTrue(len(impacts) > 0)

    def test_power_on_end_quest_for_normal_account_hero(self):
        game_tt_services.debug_clear_service()

        self.hero.is_fast = False

        self.assertEqual(places_logic.get_hero_popularity(self.hero.id).places_rating(), [])

        self.complete_quest()

        self.assertTrue(len(places_logic.get_hero_popularity(self.hero.id).places_rating()) > 0)

        impacts = politic_power_logic.get_last_power_impacts(limit=100)

        self.assertTrue(len(impacts) == 0)

    def test_power_on_end_quest_for_normal_account_hero__in_frontier(self):
        game_tt_services.debug_clear_service()

        for place in places_storage.places.all():
            place.is_frontier = True

        self.hero.is_fast = False

        self.assertEqual(places_logic.get_hero_popularity(self.hero.id).places_rating(), [])

        self.complete_quest()

        self.assertTrue(len(places_logic.get_hero_popularity(self.hero.id).places_rating()) > 0)

        impacts = politic_power_logic.get_last_power_impacts(limit=100)

        self.assertTrue(len(impacts) > 0)

    def test_get_expirience_for_quest(self):
        self.assertEqual(self.hero.experience, 0)
        self.complete_quest()
        self.assertTrue(self.hero.experience > 0)

    @mock.patch('the_tale.game.balance.formulas.experience_for_quest', lambda x: 100)
    @mock.patch('the_tale.game.heroes.statistics.Statistics.quests_done', 1)
    def test_get_expirience_for_quest__from_place(self):
        for place in places_storage.places.all():
            place.attrs.experience_bonus = 0.0
        for person in persons_storage.persons.all():
            person.attrs.experience_bonus = 0.0

        self.assertEqual(self.quest.get_expirience_for_quest(self.quest.current_info.uid, self.hero), 100)

        for place in places_storage.places.all():
            place.attrs.experience_bonus = 1.0

        self.assertTrue(self.quest.get_expirience_for_quest(self.quest.current_info.uid, self.hero) > 100)

    @mock.patch('the_tale.game.balance.formulas.experience_for_quest', lambda x: 100)
    @mock.patch('the_tale.game.heroes.statistics.Statistics.quests_done', 1)
    def test_get_expirience_for_quest__from_person(self):
        for place in places_storage.places.all():
            place.attrs.experience_bonus = 0.0
        for person in persons_storage.persons.all():
            person.attrs.experience_bonus = 0.0

        self.assertEqual(self.quest.get_expirience_for_quest(self.quest.current_info.uid, self.hero), 100)

        for person in persons_storage.persons.all():
            person.attrs.experience_bonus = 1.0

        self.assertTrue(self.quest.get_expirience_for_quest(self.quest.current_info.uid, self.hero) > 100)

    @mock.patch('the_tale.game.balance.formulas.experience_for_quest', lambda x: 100)
    @mock.patch('the_tale.game.heroes.statistics.Statistics.quests_done', 1)
    def test_get_expirience_for_quest__from_emissary(self):
        self.prepair_forum_for_clans()

        clan = self.create_clan(owner=self.account, uid=1)

        emissary = self.create_emissary(clan=clan,
                                        initiator=self.account,
                                        place_id=self.place_1.id)

        for place in places_storage.places.all():
            place.attrs.experience_bonus = 0.0

        for person in persons_storage.persons.all():
            person.attrs.experience_bonus = 0.0

        for emissary in emissaries_storage.emissaries.all():
            emissary.attrs.experience_bonus = 0.0

        self.hero.quests.pop_quest()
        self.hero.actions.pop_action()

        self.action_quest = actions_prototypes.ActionQuestPrototype.create(hero=self.hero)

        helpers.setup_quest(self.hero,
                            emissary_id=emissary.id,
                            person_action=quests_relations.PERSON_ACTION.random())
        self.quest = self.hero.quests.current_quest

        self.assertEqual(self.quest.get_expirience_for_quest(self.quest.current_info.uid, self.hero), 100)

        for emissary in emissaries_storage.emissaries.all():
            emissary.attrs.experience_bonus = 1.0

        self.assertTrue(self.quest.get_expirience_for_quest(self.quest.current_info.uid, self.hero) > 100)

    @mock.patch('the_tale.game.balance.formulas.person_power_for_quest', lambda x: 100)
    def test_get_politic_power_for_quest__from_person(self):
        for person in persons_storage.persons.all():
            person.attrs.politic_power_bonus = 0.0

        self.assertEqual(self.quest.get_politic_power_for_quest(self.quest.current_info.uid, self.hero), 100)

        for person in persons_storage.persons.all():
            person.attrs.politic_power_bonus = 1.0

        self.assertTrue(self.quest.get_politic_power_for_quest(self.quest.current_info.uid, self.hero) > 100)

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 0)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda *argv: False)
    def test_get_money_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertTrue(self.hero.statistics.money_earned_from_quests > 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

    @mock.patch('the_tale.game.balance.constants.ARTIFACTS_PER_BATTLE', 0)
    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda *argv: True)
    def test_get_artifacts_for_quest(self):
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.complete_quest()
        self.assertEqual(self.hero.statistics.money_earned_from_quests, 0)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    def test_get_upgrdade_choice__no_preference(self):
        for i in range(100):
            self.assertTrue(self.quest._get_upgrdade_choice(self.hero).is_BUY)

    def test_get_upgrdade_choice(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, heroes_relations.EQUIPMENT_SLOT.PLATE)
        self.hero.equipment.get(heroes_relations.EQUIPMENT_SLOT.PLATE).integrity = 0

        choices = set()

        for i in range(100):
            choices.add(self.quest._get_upgrdade_choice(self.hero))

        self.assertEqual(choices, set((relations.UPGRADE_EQUIPMENT_VARIANTS.BUY,
                                       relations.UPGRADE_EQUIPMENT_VARIANTS.SHARP,
                                       relations.UPGRADE_EQUIPMENT_VARIANTS.REPAIR)))

    def test_get_upgrdade_choice__no_item_equipped(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, heroes_relations.EQUIPMENT_SLOT.RING)

        for i in range(100):
            self.assertTrue(self.quest._get_upgrdade_choice(self.hero).is_BUY)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: relations.UPGRADE_EQUIPMENT_VARIANTS.BUY))
    def test_upgrade_equipment__buy(self):
        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)
        self.assertEqual(self.hero.statistics.artifacts_had, 1)

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: relations.UPGRADE_EQUIPMENT_VARIANTS.SHARP))
    def test_upgrade_equipment__sharp(self):
        old_power = self.hero.power.clone()
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(old_power.total() + 1, self.hero.power.total())

    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype._get_upgrdade_choice', classmethod(lambda *argv, **kwargs: relations.UPGRADE_EQUIPMENT_VARIANTS.REPAIR))
    def test_upgrade_equipment__repair(self):

        test_artifact = random.choice(list(self.hero.equipment.values()))
        test_artifact.integrity = 0
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.EQUIPMENT_SLOT, test_artifact.type.equipment_slot)

        old_power = self.hero.power.clone()
        self.assertEqual(self.hero.statistics.artifacts_had, 0)

        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertEqual(self.hero.statistics.artifacts_had, 0)
        self.assertEqual(old_power.total(), self.hero.power.total())
        self.assertEqual(test_artifact.integrity, test_artifact.max_integrity)

    def test_upgrade_equipment__money_limit(self):
        self.hero.money = 99999999

        self.quest._upgrade_equipment(process_message=self.quest.current_info.process_message,
                                      hero=self.hero,
                                      knowledge_base=self.quest.knowledge_base,
                                      cost=666)

        self.assertTrue(self.hero.money > 0)

    def test_modify_reward_scale(self):
        self.complete_quest(positive_results=True)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype.get_state_by_jump_pointer', lambda qp: self.quest.knowledge_base[self.quest.machine.pointer.state]):
            for person in persons_storage.persons.all():
                person.attrs.on_profite_reward_bonus = 0

            self.assertEqual(self.quest.modify_reward_scale(1), 1)

            for person in persons_storage.persons.all():
                person.attrs.on_profite_reward_bonus = 1

            self.assertTrue(self.quest.modify_reward_scale(1) > 1)

    def test_give_energy_on_reward(self):
        self.complete_quest(positive_results=True)

        time.sleep(0.1)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype.get_state_by_jump_pointer', lambda qp: self.quest.knowledge_base[self.quest.machine.pointer.state]):
            for person in persons_storage.persons.all():
                person.attrs.on_profite_energy = 0

            with self.check_not_changed(lambda: game_tt_services.energy.cmd_balance(self.hero.account_id)):
                self.quest.give_energy_on_reward()
                time.sleep(0.1)

            for person in persons_storage.persons.all():
                person.attrs.on_profite_energy = 1

            with self.check_increased(lambda: game_tt_services.energy.cmd_balance(self.hero.account_id)):
                self.quest.give_energy_on_reward()
                time.sleep(0.1)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_regenerate_energy', False)
    def test_give_energy_on_reward__energy_regeneration_restricted(self):
        self.complete_quest(positive_results=True)

        time.sleep(0.1)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype.get_state_by_jump_pointer', lambda qp: self.quest.knowledge_base[self.quest.machine.pointer.state]):
            for person in persons_storage.persons.all():
                person.attrs.on_profite_energy = 1

            with self.check_not_changed(lambda: game_tt_services.energy.cmd_balance(self.hero.account_id)):
                self.quest.give_energy_on_reward()
                time.sleep(0.1)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda hero: True)
    @mock.patch('the_tale.game.balance.constants.ARTIFACT_POWER_DELTA', 0.0)
    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.positive_results_masters', lambda self: [])
    def test_give_reward__artifact_scale(self):

        self.assertEqual(self.hero.bag.occupation, 0)

        artifacts_logic.create_random_artifact_record('just_ring', type=artifacts_relations.ARTIFACT_TYPE.RING)
        artifacts_logic.create_random_artifact_record('just_amulet', type=artifacts_relations.ARTIFACT_TYPE.AMULET)

        with mock.patch('the_tale.game.heroes.objects.Hero.receive_artifacts_choices',
                        lambda *argv, **kwargs: artifacts_storage.artifacts.artifacts_for_type([artifacts_relations.ARTIFACT_TYPE.RING])):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.0)

        with mock.patch('the_tale.game.heroes.objects.Hero.receive_artifacts_choices',
                        lambda *argv, **kwargs: artifacts_storage.artifacts.artifacts_for_type([artifacts_relations.ARTIFACT_TYPE.AMULET])):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

        self.assertEqual(self.hero.bag.occupation, 2)

        artifact_1, artifact_2 = sorted(list(self.hero.bag.values()), key=lambda artifact: artifact.bag_uuid)

        self.assertEqual(artifact_1.level + 1, artifact_2.level)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda hero: False)
    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.positive_results_masters', lambda self: [])
    def test_give_reward__money_scale(self):

        self.assertEqual(self.hero.money, 0)

        self.quest._give_reward(self.hero, 'bla-bla', scale=1.0)

        not_scaled_money = self.hero.money

        self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

        self.assertEqual(self.hero.money - not_scaled_money, int(f.sell_artifact_price(self.hero.level) * 1.5))

    @mock.patch('the_tale.game.heroes.objects.Hero.can_get_artifact_for_quest', lambda hero: False)
    @mock.patch('the_tale.game.heroes.objects.Hero.quest_money_reward_multiplier', lambda hero: -100)
    @mock.patch('the_tale.game.quests.prototypes.QuestPrototype.positive_results_masters', lambda self: [])
    def test_give_reward__money_scale_less_then_zero(self):

        with self.check_delta(lambda: self.hero.money, 1):
            self.quest._give_reward(self.hero, 'bla-bla', scale=1.5)

    def test_finish_quest__person_personality(self):
        result = random.choice([questgen_quests_base_quest.RESULTS.SUCCESSED, questgen_quests_base_quest.RESULTS.FAILED])
        cosmetic = random.choice([persons_relations.PERSONALITY_COSMETIC.TRUTH_SEEKER,
                                  persons_relations.PERSONALITY_COSMETIC.KNAVE,
                                  persons_relations.PERSONALITY_COSMETIC.GOOD_SOUL,
                                  persons_relations.PERSONALITY_COSMETIC.BULLY])

        for person in persons_storage.persons.all():
            person.personality_cosmetic = cosmetic
            person.refresh_attributes()

        quest_results = {fact.uid: result
                         for fact in self.quest.knowledge_base.filter(questgen_facts.Person)}

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest._finish_quest(mock.Mock(results=quest_results), self.hero)

        self.assertEqual(update_habits.call_args_list,
                         [mock.call(cosmetic.effect.value[result])] * len(quest_results))

    @mock.patch('the_tale.game.heroes.objects.Hero.experience_modifier', 2)
    def test_finish_quest__add_bonus_experience(self):

        self.quest.current_info.experience = 10
        self.quest.current_info.experience_bonus = 1

        # we don't modify power bonus like main power, becouse of possible experience_modifier < 1
        with self.check_delta(lambda: self.hero.experience, 21):
            self.quest._finish_quest(mock.Mock(results=mock.Mock(items=lambda: [])), self.hero)

    def test_finish_quest__add_companion_experience(self):
        companion_record = next(companions_storage.companions.enabled_companions())
        companion = companions_logic.create_companion(companion_record)
        companion.coherence = 50

        self.hero.set_companion(companion)

        with self.check_increased(lambda: self.hero.companion.experience):
            with self.check_not_changed(lambda: self.hero.companion.coherence):
                self.quest._finish_quest(mock.Mock(results=mock.Mock(items=lambda: [])), self.hero)

    @mock.patch('the_tale.game.heroes.objects.Hero.is_premium', True)
    def test_give_power__add_bonus_power(self):

        self.quest.current_info.power = 10
        self.quest.current_info.power_bonus = 1

        self.assertEqual(self.quest.get_current_power(2), 20)


class InterpreterCallbacksTests(PrototypeTestsBase):

    def setUp(self):
        super(InterpreterCallbacksTests, self).setUp()

    def test_all_callbacks_exists(self):
        for method_name in questgen_logic.get_required_interpreter_methods():
            self.assertTrue(hasattr(self.quest, method_name))

    def test_on_jump_end__only_one_marker_from_group(self):
        all_markers = {}
        for group in questgen_relations.OPTION_MARKERS_GROUPS:
            for marker in group:
                all_markers[marker] = random.choice([True, False])

        self.quest.current_info.used_markers = all_markers

        self.assertEqual(set(self.quest.current_info.used_markers.keys()), set([questgen_relations.OPTION_MARKERS.HONORABLE,
                                                                                questgen_relations.OPTION_MARKERS.DISHONORABLE,
                                                                                questgen_relations.OPTION_MARKERS.AGGRESSIVE,
                                                                                questgen_relations.OPTION_MARKERS.UNAGGRESSIVE]))

        jump = questgen_facts.Option(state_from='state_from', state_to='state_to', markers=[questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)

        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        self.assertEqual(set(self.quest.current_info.used_markers.keys()), set([questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE]))

    def test_update_habits__on_jump_end__after_actions__no_markers__default(self):
        jump = questgen_facts.Jump(state_from='state_from', state_to='state_to')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions__wrong_markers__default(self):
        jump = questgen_facts.Option(state_from='state_from', state_to='state_to', markers=[666, 75], type='opt')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions__default(self):
        jump = questgen_facts.Option(state_from='state_from', state_to='state_to', markers=[questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        self.assertEqual(self.quest.current_info.used_markers,
                         {questgen_relations.OPTION_MARKERS.HONORABLE: True,
                          questgen_relations.OPTION_MARKERS.AGGRESSIVE: True})

    def test_finish_quest__update_habits__defaults(self):
        jump = questgen_facts.Option(state_from='state_from', state_to='state_to', markers=[questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=True)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_state__after_actions(questgen_facts.Finish(uid='test_uid',
                                                                     start='any_start_uid',
                                                                     results={},
                                                                     nesting=666))

        self.assertEqual(update_habits.call_args_list, [mock.call(heroes_relations.HABIT_CHANGE_SOURCE.QUEST_HONORABLE_DEFAULT),
                                                        mock.call(heroes_relations.HABIT_CHANGE_SOURCE.QUEST_AGGRESSIVE_DEFAULT)])

    def test_update_habits__on_jump_end__after_actions__no_markers(self):
        jump = questgen_facts.Jump(state_from='state_from', state_to='state_to')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions__wrong_markers(self):
        jump = questgen_facts.Option(state_from='state_from', state_to='state_to', markers=[666, 75], type='opt')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_jump_end__after_actions(jump)
        self.assertEqual(update_habits.call_args_list, [])

    def test_update_habits__on_jump_end__after_actions(self):
        jump = questgen_facts.Option(state_from='state_from', state_to='state_to', markers=[questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        self.assertEqual(self.quest.current_info.used_markers,
                         {questgen_relations.OPTION_MARKERS.HONORABLE: False,
                          questgen_relations.OPTION_MARKERS.AGGRESSIVE: False})

    def test_finish_quest__update_habits__custom(self):

        jump = questgen_facts.Option(state_from='state_from', state_to='state_to', markers=[questgen_relations.OPTION_MARKERS.HONORABLE, questgen_relations.OPTION_MARKERS.AGGRESSIVE], type='opt')
        path = questgen_facts.ChoicePath(choice='some_choice', option=jump.uid, default=False)
        self.quest.knowledge_base += path

        self.quest.on_jump_end__after_actions(jump)

        with mock.patch('the_tale.game.heroes.objects.Hero.update_habits') as update_habits:
            self.quest.on_state__after_actions(questgen_facts.Finish(uid='test_uid',
                                                                     start='any_start_uid',
                                                                     results={},
                                                                     nesting=666))

        self.assertEqual(update_habits.call_args_list, [mock.call(heroes_relations.HABIT_CHANGE_SOURCE.QUEST_HONORABLE),
                                                        mock.call(heroes_relations.HABIT_CHANGE_SOURCE.QUEST_AGGRESSIVE)])


class CheckRequirementsTests(PrototypeTestsBase):

    def setUp(self):
        super(CheckRequirementsTests, self).setUp()

        self.hero_fact = next(self.quest.knowledge_base.filter(questgen_facts.Hero))
        self.person_fact = next(self.quest.knowledge_base.filter(questgen_facts.Person))

        self.person = persons_storage.persons[self.person_fact.externals['id']]

        self.place_1_fact = logic.fact_place(self.place_1)
        self.place_2_fact = logic.fact_place(self.place_2)
        self.place_3_fact = logic.fact_place(self.place_3)

        for fact in [self.place_1_fact, self.place_2_fact, self.place_3_fact]:
            if fact.uid not in self.quest.knowledge_base:
                self.quest.knowledge_base += fact

    def get_check_places(self, place_id):
        for place in self.quest.knowledge_base.filter(questgen_facts.Place):
            if places_storage.places[place.externals['id']].id == place_id:
                place_fact = place
                break

        for place in self.quest.knowledge_base.filter(questgen_facts.Place):
            if places_storage.places[place.externals['id']].id != place_id:
                non_place_fact = place
                break

        return place_fact, non_place_fact

    # located in

    def check_located_in(self, object, place, result):
        requirement = questgen_requirements.LocatedIn(object=object.uid, place=place.uid)
        self.assertEqual(self.quest.check_located_in(requirement), result)

    def test_check_located_in__person(self):
        person_place_fact, nonperson_place_fact = self.get_check_places(self.person.place_id)

        self.check_located_in(object=self.person_fact, place=person_place_fact, result=True)
        self.check_located_in(object=self.person_fact, place=nonperson_place_fact, result=False)

    def test_check_located_in__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero
        self.check_located_in(object=wrong_hero, place=next(self.quest.knowledge_base.filter(questgen_facts.Place)), result=False)

    def test_check_located_in__hero__in_place(self):
        self.hero.position.set_place(self.place_1)

        self.check_located_in(object=self.hero_fact, place=self.place_1_fact, result=True)
        self.check_located_in(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_in__hero__move_near(self):
        self.hero.position.set_position(self.place_1.x + 0.5, self.place_1.y + 0.5)

        self.check_located_in(object=self.hero_fact, place=self.place_1_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_in__hero__road(self):
        places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

        path = map_storage.cells.find_path_to_place(from_x=self.place_1.x,
                                                    from_y=self.place_1.y,
                                                    to_place_id=self.place_2.id,
                                                    cost_modifiers=places_cost_modifiers,
                                                    risk_level=self.hero.preferences.risk_level)
        self.hero.position.set_position(*path.coordinates(0.5))

        self.check_located_in(object=self.hero_fact, place=self.place_1_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_in(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_in__wrong_requirement(self):
        place_uid = next(self.quest.knowledge_base.filter(questgen_facts.Place)).uid
        requirement = questgen_requirements.LocatedIn(object=place_uid, place=place_uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_located_in, requirement)

    # located near

    def check_located_near(self, object, place, result):
        requirement = questgen_requirements.LocatedNear(object=object.uid, place=place.uid)
        self.assertEqual(self.quest.check_located_near(requirement), result)

    def test_check_located_near__person(self):
        person_place_fact, nonperson_place_fact = self.get_check_places(self.person.place_id)

        self.check_located_near(object=self.person_fact, place=person_place_fact, result=False)
        self.check_located_near(object=self.person_fact, place=nonperson_place_fact, result=False)

    def test_check_located_near__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero
        self.check_located_near(object=wrong_hero, place=next(self.quest.knowledge_base.filter(questgen_facts.Place)), result=False)

    def test_check_located_near__hero__in_place(self):
        self.hero.position.set_place(self.place_1)

        self.check_located_near(object=self.hero_fact, place=self.place_1_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_near__hero__move_near(self):
        self.hero.position.set_position(self.place_1.x + 0.4, self.place_1.y + 0.4)

        self.check_located_near(object=self.hero_fact, place=self.place_1_fact, result=True)
        self.check_located_near(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_near__hero__road(self):
        places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

        path = map_storage.cells.find_path_to_place(from_x=self.place_1.x,
                                                    from_y=self.place_1.y,
                                                    to_place_id=self.place_2.id,
                                                    cost_modifiers=places_cost_modifiers,
                                                    risk_level=self.hero.preferences.risk_level)
        self.hero.position.set_position(*path.coordinates(0.1))

        self.check_located_near(object=self.hero_fact, place=self.place_1_fact, result=True)
        self.check_located_near(object=self.hero_fact, place=self.place_2_fact, result=False)
        self.check_located_near(object=self.hero_fact, place=self.place_3_fact, result=False)

    def test_check_located_near__wrong_requirement(self):
        place_uid = next(self.quest.knowledge_base.filter(questgen_facts.Place)).uid
        requirement = questgen_requirements.LocatedNear(object=place_uid, place=place_uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_located_near, requirement)

    # located on road

    def check_located_on_road(self, object, place_from, place_to, percents, result):
        requirement = questgen_requirements.LocatedOnRoad(object=object.uid,
                                                          place_from=place_from.uid,
                                                          place_to=place_to.uid,
                                                          percents=percents)
        self.assertEqual(self.quest.check_located_on_road(requirement), result)

    def test_check_located_on_road__person(self):
        person_place_fact, nonperson_place_fact = self.get_check_places(self.person.place_id)

        self.check_located_on_road(object=self.person_fact, place_from=person_place_fact, place_to=nonperson_place_fact, percents=0.02, result=False)
        self.check_located_on_road(object=self.person_fact, place_from=person_place_fact, place_to=nonperson_place_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.person_fact, place_from=nonperson_place_fact, place_to=person_place_fact, percents=0.02, result=False)
        self.check_located_on_road(object=self.person_fact, place_from=nonperson_place_fact, place_to=person_place_fact, percents=0.99, result=False)

    def test_check_located_on_road__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        self.check_located_on_road(object=wrong_hero, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.02, result=False)
        self.check_located_on_road(object=wrong_hero, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=wrong_hero, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.02, result=False)
        self.check_located_on_road(object=wrong_hero, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=False)

    def test_check_located_on_road__hero__in_place(self):
        self.hero.position.set_place(self.place_1)

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=1, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=1, result=True)

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.02, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.02, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=True)

    def test_check_located_on_road__hero__move_near(self):
        self.hero.position.set_position(self.place_1.x + 0.5, self.place_1.y + 0.5)

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.02, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.02, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=False)

    def test_check_located_on_road__hero__road(self):
        places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

        path = map_storage.cells.find_path_to_place(from_x=self.place_1.x,
                                                    from_y=self.place_1.y,
                                                    to_place_id=self.place_2.id,
                                                    cost_modifiers=places_cost_modifiers,
                                                    risk_level=self.hero.preferences.risk_level)
        self.hero.position.set_position(*path.coordinates(0.25))

        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.02, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_1_fact, place_to=self.place_2_fact, percents=0.99, result=False)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.02, result=True)
        self.check_located_on_road(object=self.hero_fact, place_from=self.place_2_fact, place_to=self.place_1_fact, percents=0.99, result=False)

    def test_check_located_on_road__wrong_requirement(self):
        requirement = questgen_requirements.LocatedOnRoad(object=self.place_1_fact.uid, place_from=self.place_2_fact.uid, place_to=self.place_3_fact.uid, percents=0.25)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_located_on_road, requirement)

    # has money

    def test_check_has_money__person(self):
        requirement = questgen_requirements.HasMoney(object=self.person_fact.uid, money=666)
        self.assertFalse(self.quest.check_has_money(requirement))

    def test_check_has_money__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = questgen_requirements.HasMoney(object=wrong_hero.uid, money=666)
        self.assertFalse(self.quest.check_has_money(requirement))

    def test_check_has_money__hero(self):
        requirement = questgen_requirements.HasMoney(object=self.hero_fact.uid, money=666)
        self.assertFalse(self.quest.check_has_money(requirement))

        self.hero.money = 667
        self.assertTrue(self.quest.check_has_money(requirement))

    def test_check_has_money__wrong_requirement(self):
        requirement = questgen_requirements.HasMoney(object=self.place_1_fact.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_has_money, requirement)

    # is alive

    def test_check_is_alive__person(self):
        requirement = questgen_requirements.IsAlive(object=self.person_fact.uid)
        self.assertTrue(self.quest.check_is_alive(requirement))

    def test_check_is_alive__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = questgen_requirements.IsAlive(object=wrong_hero.uid)
        self.assertFalse(self.quest.check_is_alive(requirement))

    def test_check_is_alive__hero(self):
        requirement = questgen_requirements.IsAlive(object=self.hero_fact.uid)
        self.assertTrue(self.quest.check_is_alive(requirement))

        self.hero.kill()
        self.assertFalse(self.quest.check_is_alive(requirement))

    def test_check_is_alive__wrong_requirement(self):
        requirement = questgen_requirements.IsAlive(object=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.check_is_alive, requirement)


class SatisfyRequirementsTests(PrototypeTestsBase):

    def setUp(self):
        super(SatisfyRequirementsTests, self).setUp()

        self.hero_fact = next(self.quest.knowledge_base.filter(questgen_facts.Hero))
        self.person_fact = next(self.quest.knowledge_base.filter(questgen_facts.Person))

        self.person = persons_storage.persons[self.person_fact.externals['id']]

        self.place_1_fact = logic.fact_place(self.place_1)
        self.place_2_fact = logic.fact_place(self.place_2)
        self.place_3_fact = logic.fact_place(self.place_3)

        for fact in [self.place_1_fact, self.place_2_fact, self.place_3_fact]:
            if fact.uid not in self.quest.knowledge_base:
                self.quest.knowledge_base += fact

    def get_check_places(self, place_id):
        for place in self.quest.knowledge_base.filter(questgen_facts.Place):
            if places_storage.places[place.externals['id']].id == place_id:
                place_fact = place
                break

        for place in self.quest.knowledge_base.filter(questgen_facts.Place):
            if places_storage.places[place.externals['id']].id != place_id:
                non_place_fact = place
                break

        return place_fact, non_place_fact

    # located in

    def test_satisfy_located_in__moved_person(self):
        wrong_place_fact_uid = self.place_1_fact.uid if self.person.place_id != self.place_1.id else self.place_2_fact.uid
        right_place_fact_uid = uids.place(self.person.place_id)

        requirement = questgen_requirements.LocatedIn(object=self.person_fact.uid, place=wrong_place_fact_uid)

        for state in self.quest.knowledge_base.filter(questgen_facts.State):
            state.require = tuple(list(state.require) + [questgen_requirements.LocatedIn(object=self.person_fact.uid, place=wrong_place_fact_uid)])

        self.quest.satisfy_located_in(requirement)

        self.assertEqual(requirement.object, self.person_fact.uid)
        self.assertEqual(requirement.place, wrong_place_fact_uid)

        for state in self.quest.knowledge_base.filter(questgen_facts.State):
            in_base_requirement = state.require[-1]

            self.assertEqual(in_base_requirement.object, self.person_fact.uid)
            self.assertEqual(in_base_requirement.place, right_place_fact_uid)

    def test_satisfy_located_in__non_hero(self):
        requirement = questgen_requirements.LocatedIn(object=self.place_2_fact.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_in, requirement)

    def test_satisfy_located_in__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = questgen_requirements.LocatedIn(object=wrong_hero.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_in, requirement)

    def test_satisfy_located_in__success(self):
        self.hero.position.set_place(self.place_1)

        requirement = questgen_requirements.LocatedIn(object=self.hero_fact.uid, place=self.place_2_fact.uid)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_to') as move_hero_to:
            self.quest.satisfy_located_in(requirement)

        self.assertEqual(move_hero_to.call_args_list, [mock.call(destination=self.place_2)])

    # located near

    def test_satisfy_located_near__non_hero(self):
        requirement = questgen_requirements.LocatedNear(object=self.person_fact.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_near, requirement)

    def test_satisfy_located_near__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = questgen_requirements.LocatedNear(object=wrong_hero.uid, place=self.place_1_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_near, requirement)

    def test_satisfy_located_near__success(self):
        requirement = questgen_requirements.LocatedNear(object=self.hero_fact.uid, place=self.place_2_fact.uid, terrains=[1, 2])

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_near') as move_hero_near:
            self.quest.satisfy_located_near(requirement)

        self.assertEqual(move_hero_near.call_args_list, [mock.call(destination=self.place_2, terrains=[1, 2])])

    def test_satisfy_located_near__no_place(self):
        requirement = questgen_requirements.LocatedNear(object=self.hero_fact.uid, place=None, terrains=[1, 2])

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_near') as move_hero_near:
            self.quest.satisfy_located_near(requirement)

        self.assertEqual(move_hero_near.call_args_list, [mock.call(destination=None, terrains=[1, 2])])

    # located on road

    def test_satisfy_located_on_road__non_hero(self):
        requirement = questgen_requirements.LocatedOnRoad(object=self.person_fact.uid, place_from=self.place_1_fact.uid, place_to=self.place_2_fact.uid, percents=0.5)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_on_road, requirement)

    def test_satisfy_located_on_road__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = questgen_requirements.LocatedOnRoad(object=wrong_hero.uid, place_from=self.place_1_fact.uid, place_to=self.place_2_fact.uid, percents=0.5)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_located_on_road, requirement)

    def test_satisfy_located_on_road__success(self):
        requirement = questgen_requirements.LocatedOnRoad(object=self.hero_fact.uid, place_from=self.place_1_fact.uid, place_to=self.place_2_fact.uid, percents=0.5)

        with mock.patch('the_tale.game.quests.prototypes.QuestPrototype._move_hero_on_road') as move_hero_on_road:
            self.quest.satisfy_located_on_road(requirement)

        self.assertEqual(move_hero_on_road.call_args_list, [mock.call(place_from=self.place_1,
                                                                      place_to=self.place_2,
                                                                      percents=0.5)])

    # located has money

    def test_satisfy_has_money__non_hero(self):
        requirement = questgen_requirements.HasMoney(object=self.person_fact.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_has_money, requirement)

    def test_satisfy_has_money__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = questgen_requirements.HasMoney(object=wrong_hero.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_has_money, requirement)

    def test_satisfy_has_money__success(self):
        requirement = questgen_requirements.HasMoney(object=self.hero_fact.uid, money=666)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_has_money, requirement)

    # located is alive

    def test_satisfy_is_alive__non_hero(self):
        requirement = questgen_requirements.IsAlive(object=self.person_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_is_alive, requirement)

    def test_satisfy_is_alive__wrong_hero(self):
        wrong_hero = questgen_facts.Hero(uid='wrong_hero', externals={'id': 666})
        self.quest.knowledge_base += wrong_hero

        requirement = questgen_requirements.IsAlive(object=wrong_hero.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_is_alive, requirement)

    def test_satisfy_is_alive__success(self):
        requirement = questgen_requirements.IsAlive(object=self.hero_fact.uid)
        self.assertRaises(exceptions.UnknownRequirementError, self.quest.satisfy_is_alive, requirement)


class PrototypeMoveHeroTests(PrototypeTestsBase):

    def setUp(self):
        super(PrototypeMoveHeroTests, self).setUp()

    # move hero to

    def test_move_hero_to__from_walking(self):
        self.hero.position.set_position(self.place_1.x + 0.5, self.place_1.y + 0.5)

        self.quest._move_hero_to(self.place_1)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertTrue(self.hero.actions.current_action.destination_id, self.place_1.id)
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_1.id)

        self.assertEqual(self.hero.actions.current_action.path.destination_coordinates(),
                         (self.place_1.x, self.place_1.y))

    def test_move_hero_to__from_road(self):
        places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

        path = map_storage.cells.find_path_to_place(from_x=self.place_1.x,
                                                    from_y=self.place_1.y,
                                                    to_place_id=self.place_2.id,
                                                    cost_modifiers=places_cost_modifiers,
                                                    risk_level=self.hero.preferences.risk_level)
        self.hero.position.set_position(*path.coordinates(0.5))

        self.quest._move_hero_to(self.place_3)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.break_at, None)

        self.assertEqual(self.hero.actions.current_action.path.destination_coordinates(),
                         (self.place_3.x, self.place_3.y))

    def test_move_hero_to__from_place(self):
        self.hero.position.set_place(self.place_1)

        self.quest._move_hero_to(self.place_3)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.break_at, None)

        self.assertEqual(self.hero.actions.current_action.path.destination_coordinates(),
                         (self.place_3.x, self.place_3.y))

    # move hero near

    def test_move_hero_near__from_walking(self):
        self.hero.position.set_position(self.place_1.x + 0.5, self.place_1.y + 0.5)

        self.quest._move_hero_near(self.place_1)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_1.id)
        self.assertNotEqual(self.hero.actions.current_action.path.destination_coordinates(),
                            (self.place_1.x, self.place_1.y))

    def test_move_hero_near__from_road(self):
        places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

        path = map_storage.cells.find_path_to_place(from_x=self.place_1.x,
                                                    from_y=self.place_1.y,
                                                    to_place_id=self.place_2.id,
                                                    cost_modifiers=places_cost_modifiers,
                                                    risk_level=self.hero.preferences.risk_level)
        self.hero.position.set_position(*path.coordinates(0.5))

        self.quest._move_hero_near(self.place_3)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertNotEqual(self.hero.actions.current_action.path.destination_coordinates(),
                            (self.place_3.x, self.place_3.y))

    def test_move_hero_near__from_place(self):
        self.hero.position.set_place(self.place_1)

        self.quest._move_hero_near(self.place_1)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.place.id, self.place_1.id)
        self.assertNotEqual(self.hero.actions.current_action.path.destination_coordinates(),
                            (self.place_1.x, self.place_1.y))

    # move hero on road

    def test_move_hero_on_road__from_walking(self):
        self.hero.position.set_position(self.place_1.x + 0.5, self.place_1.y + 0.5)

        self.quest._move_hero_on_road(place_from=self.place_1, place_to=self.place_3, percents=0.9)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.destination_id, self.place_3.id)
        self.assertEqual(self.hero.actions.current_action.path.destination_coordinates(),
                         (self.place_3.x, self.place_3.y))

    def test_move_hero_on_road__from_road(self):
        places_cost_modifiers = heroes_logic.get_places_path_modifiers(hero=self.hero)

        path = map_storage.cells.find_path_to_place(from_x=self.place_1.x,
                                                    from_y=self.place_1.y,
                                                    to_place_id=self.place_2.id,
                                                    cost_modifiers=places_cost_modifiers,
                                                    risk_level=self.hero.preferences.risk_level)
        self.hero.position.set_position(*path.coordinates(0.5))

        self.quest._move_hero_on_road(place_from=self.place_1, place_to=self.place_3, percents=0.9)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertTrue(0 < self.hero.actions.current_action.break_at < 0.9)
        self.assertEqual(self.hero.actions.current_action.path.destination_coordinates(),
                         (self.place_3.x, self.place_3.y))

    def test_move_hero_on_road__from_place(self):
        self.hero.position.set_place(self.place_1)

        self.quest._move_hero_on_road(place_from=self.place_1, place_to=self.place_3, percents=0.9)

        self.assertTrue(self.hero.actions.current_action.TYPE.is_MOVE_SIMPLE)
        self.assertEqual(self.hero.actions.current_action.destination.id, self.place_3.id)
        self.assertEqual(round(self.hero.actions.current_action.break_at, 4), 0.9000)
        self.assertEqual(self.hero.actions.current_action.path.destination_coordinates(),
                         (self.place_3.x, self.place_3.y))
