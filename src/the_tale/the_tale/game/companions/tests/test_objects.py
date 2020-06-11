
import smart_imports

smart_imports.all()


class CompanionTests(utils_testcase.TestCase):

    def setUp(self):
        super(CompanionTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.companion_record = logic.create_companion_record(utg_name=game_names.generator().get_test_name(),
                                                              description='description',
                                                              type=tt_beings_relations.TYPE.random(),
                                                              max_health=10,
                                                              dedication=relations.DEDICATION.random(),
                                                              archetype=game_relations.ARCHETYPE.random(),
                                                              mode=relations.MODE.random(),
                                                              abilities=companions_abilities_container.Container(),
                                                              communication_verbal=tt_beings_relations.COMMUNICATION_VERBAL.random(),
                                                              communication_gestures=tt_beings_relations.COMMUNICATION_GESTURES.random(),
                                                              communication_telepathic=tt_beings_relations.COMMUNICATION_TELEPATHIC.random(),
                                                              intellect_level=tt_beings_relations.INTELLECT_LEVEL.random(),
                                                              structure=tt_beings_relations.STRUCTURE.random(),
                                                              features=frozenset((tt_beings_relations.FEATURE.random(), tt_beings_relations.FEATURE.random())),
                                                              movement=tt_beings_relations.MOVEMENT.random(),
                                                              body=tt_beings_relations.BODY.random(),
                                                              size=tt_beings_relations.SIZE.random(),
                                                              orientation=tt_beings_relations.ORIENTATION.random(),
                                                              weapons=[artifacts_objects.Weapon(weapon=artifacts_relations.STANDARD_WEAPON.random(),
                                                                                                material=tt_artifacts_relations.MATERIAL.random(),
                                                                                                power_type=artifacts_relations.ARTIFACT_POWER_TYPE.random())],
                                                              state=relations.STATE.ENABLED)
        self.hero.set_companion(logic.create_companion(self.companion_record))
        self.companion = self.hero.companion

    def test_initialization(self):
        self.assertEqual(self.companion.health, 10)
        self.assertEqual(self.companion.experience, 0)
        self.assertEqual(self.companion.coherence, c.COMPANIONS_MIN_COHERENCE)

    def test_serialization(self):
        self.assertEqual(self.companion.serialize(),
                         objects.Companion.deserialize(self.companion.serialize()).serialize())

    def test_experience_to_next_level(self):
        self.assertEqual(self.companion.experience_to_next_level, f.companions_coherence_for_level(1))

        self.companion.coherence = 5
        self.assertEqual(self.companion.experience_to_next_level, f.companions_coherence_for_level(6))

    def test_experience_to_next_level__max_level(self):
        self.companion.coherence = c.COMPANIONS_MAX_COHERENCE - 1

        with self.check_not_changed(lambda: self.companion.experience_to_next_level):
            self.companion.coherence = c.COMPANIONS_MAX_COHERENCE

    def test_add_experience__coherence_speed(self):
        self.companion.coherence = 95

        with self.check_delta(lambda: self.companion.experience, 10):
            self.companion.add_experience(10)

        with mock.patch('the_tale.game.heroes.objects.Hero.companion_coherence_speed', 2):
            with self.check_delta(lambda: self.companion.experience, 20):
                self.companion.add_experience(10)

    def test_add_experience__level_not_changed(self):
        self.companion.coherence = 5

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            with self.check_not_changed(lambda: self.companion.coherence):
                self.companion.add_experience(1)

        self.assertEqual(reset_accessors_cache.call_count, 0)

        self.assertEqual(self.companion.experience, 1)

    def test_add_experience__level_changed(self):
        self.companion.coherence = 5

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            with self.check_delta(lambda: self.companion.coherence, 1):
                self.companion.add_experience(self.companion.experience_to_next_level + 2)

        self.assertEqual(reset_accessors_cache.call_count, 1)

        self.assertEqual(self.companion.experience, 2)

    def test_add_experience__2_levels_changed(self):
        self.companion.coherence = 5

        with self.check_delta(lambda: self.companion.coherence, 2):
            self.companion.add_experience(self.companion.experience_to_next_level + f.companions_coherence_for_level(7) + 2)

        self.assertEqual(self.companion.experience, 2)

    @mock.patch('the_tale.game.companions.objects.Companion.max_coherence', c.COMPANIONS_MAX_COHERENCE)
    def test_add_experience__max_level(self):
        self.companion.coherence = 1

        self.companion.add_experience(66666666666)

        self.assertEqual(self.companion.coherence, c.COMPANIONS_MAX_COHERENCE)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

    def test_add_experience__max_level__not_changed(self):
        self.companion.coherence = c.COMPANIONS_MAX_COHERENCE

        with self.check_not_changed(lambda: self.companion.coherence):
            self.companion.add_experience(66666666666)

        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

    def test_add_experience__max_level__not_changed__force(self):
        self.companion.coherence = c.COMPANIONS_MAX_COHERENCE

        with self.check_not_changed(lambda: self.companion.coherence):
            self.companion.add_experience(66666666666, force=True)

        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

    @mock.patch('the_tale.game.companions.objects.Companion.max_coherence', c.COMPANIONS_MAX_COHERENCE / 2)
    def test_add_experience__max_level_restricted(self):
        self.companion.coherence = 1

        self.companion.add_experience(66666666666)

        self.assertEqual(self.companion.coherence, c.COMPANIONS_MAX_COHERENCE / 2)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level - 1)

    @mock.patch('the_tale.game.companions.objects.Companion.max_coherence', c.COMPANIONS_MAX_COHERENCE / 2)
    def test_add_experience__max_level_restricted__force(self):
        self.companion.coherence = 1

        self.companion.add_experience(66666666666, force=True)

        self.assertEqual(self.companion.coherence, c.COMPANIONS_MAX_COHERENCE)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level)

    def test_max_health(self):

        max_health = self.companion.max_health

        with self.check_delta(lambda: max_health, max_health * 0.5):
            with mock.patch('the_tale.game.heroes.objects.Hero.companion_max_health_multiplier', 1.5):
                max_health = self.companion.max_health

    def test_on_accessors_cache_changed(self):
        self.companion.health = 1
        self.companion.on_accessors_cache_changed()
        self.assertEqual(self.companion.health, 1)

        self.companion.health = self.companion.max_health + 1
        self.companion.on_accessors_cache_changed()
        self.assertEqual(self.companion.health, self.companion.max_health)

    def test_max_coherence(self):

        max_coherence = self.companion.max_coherence

        with self.check_delta(lambda: max_coherence, 40):
            with mock.patch('the_tale.game.heroes.objects.Hero.companion_max_coherence', 60):
                max_coherence = self.companion.max_coherence

    def test_has_full_experience(self):

        self.assertFalse(self.companion.has_full_experience())

        self.companion.coherence = 1

        with mock.patch('the_tale.game.companions.objects.Companion.max_coherence', c.COMPANIONS_MAX_COHERENCE / 2):
            self.companion.add_experience(66666666666)
            self.assertFalse(self.companion.has_full_experience())

        self.assertEqual(self.companion.coherence, c.COMPANIONS_MAX_COHERENCE / 2)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level - 1)

        self.assertFalse(self.companion.has_full_experience())

        with mock.patch('the_tale.game.companions.objects.Companion.max_coherence', c.COMPANIONS_MAX_COHERENCE):
            self.companion.add_experience(66666666666)
            self.assertTrue(self.companion.has_full_experience())

        self.assertTrue(self.companion.has_full_experience())

    def test_coherence_greater_then_maximum(self):

        with mock.patch('the_tale.game.heroes.objects.Hero.companion_max_coherence', 60):
            self.companion.add_experience(6666666)
            self.assertEqual(self.companion.experience, self.companion.experience_to_next_level - 1)

        self.assertEqual(self.companion.max_coherence, 20)
        self.assertEqual(self.companion.coherence, 60)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level - 1)

        self.companion.add_experience(6666666666666)

        self.assertEqual(self.companion.max_coherence, 20)
        self.assertEqual(self.companion.coherence, 60)
        self.assertEqual(self.companion.experience, self.companion.experience_to_next_level - 1)

    def test_modify_attribute(self):
        checked_abilities = [ability
                             for ability in heroes_abilities_companions.ABILITIES.values()
                             if issubclass(ability, heroes_abilities_companions._CompanionAbilityModifier)]

        for ability_class in checked_abilities:
            for companion_ability in companions_abilities_effects.ABILITIES.records:
                if ability_class.EFFECT_TYPE != companion_ability.effect.TYPE.metatype:
                    continue

                if hasattr(companion_ability.effect, 'ABILITY'):  # skip battle abilities
                    continue

                if companion_ability.effect.MODIFIER is None:  # skip complex abilities
                    continue

                self.hero.abilities.reset()
                self.hero.reset_accessors_cache()

                self.companion_record.abilities = companions_abilities_container.Container(start=(companion_ability,))

                with self.check_changed(lambda: self.companion.modify_attribute(companion_ability.effect.MODIFIER, companion_ability.effect.MODIFIER.default())):
                    self.hero.abilities.add(ability_class.get_id(), random.randint(1, ability_class.MAX_LEVEL))

    def test_actual_coherence(self):
        self.companion.coherence = 50

        with mock.patch('the_tale.game.companions.objects.Companion.max_coherence', 20):
            self.assertEqual(self.companion.actual_coherence, 20)

        with mock.patch('the_tale.game.companions.objects.Companion.max_coherence', 70):
            self.assertEqual(self.companion.actual_coherence, 50)

    def test_modification_coherence(self):
        self.companion.coherence = 50

        with mock.patch('the_tale.game.companions.objects.Companion.max_coherence', 20):
            self.assertEqual(self.companion.modification_coherence(heroes_relations.MODIFIERS.COMPANION_MAX_COHERENCE), 50)
            self.assertEqual(self.companion.modification_coherence(heroes_relations.MODIFIERS.random(exclude=(heroes_relations.MODIFIERS.COMPANION_MAX_COHERENCE,))), 20)

        with mock.patch('the_tale.game.companions.objects.Companion.max_coherence', 70):
            self.assertEqual(self.companion.modification_coherence(heroes_relations.MODIFIERS.COMPANION_MAX_COHERENCE), 50)
            self.assertEqual(self.companion.modification_coherence(heroes_relations.MODIFIERS.random(exclude=(heroes_relations.MODIFIERS.COMPANION_MAX_COHERENCE,))), 50)

    @mock.patch('the_tale.game.balance.constants.COMPANIONS_HEALS_IN_HOUR', 1)
    def test_need_heal(self):
        self.companion.healed_at_turn -= c.TURNS_IN_HOUR
        self.companion.health = self.companion.max_health

        self.assertFalse(self.companion.need_heal)

        self.companion.health -= 1

        self.assertTrue(self.companion.need_heal)

    @mock.patch('the_tale.game.balance.constants.COMPANIONS_HEALS_IN_HOUR', 1)
    def test_need_heal__no_time(self):
        self.companion.healed_at_turn -= c.TURNS_IN_HOUR / 2
        self.companion.health = self.companion.max_health

        self.assertFalse(self.companion.need_heal)

        self.companion.health -= 1

        self.assertFalse(self.companion.need_heal)

    def test_heal__less_then_zero(self):
        with self.assertRaises(exceptions.HealCompanionForNegativeValueError):
            self.companion.heal(-1)

    def test_heal(self):
        self.companion.health = 1
        self.assertEqual(self.companion.heal(5), 5)
        self.assertEqual(self.companion.health, 6)

    def test_heal__overheal(self):
        self.companion.health = self.companion.max_health - 2
        self.assertEqual(self.companion.heal(5), 2)
        self.assertEqual(self.companion.health, self.companion.max_health)

    def test_heal__resurrect(self):
        self.companion.health = 0

        with mock.patch('the_tale.game.heroes.objects.Hero.reset_accessors_cache') as reset_accessors_cache:
            self.assertEqual(self.companion.heal(5), 5)

        self.assertEqual(self.companion.health, 5)
        self.assertEqual(reset_accessors_cache.call_count, 1)

    def test_defend_in_battle_probability__hero_dedication(self):
        self.hero.set_companion(self.companion)

        with self.check_increased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.COMPANION_DEDICATION, heroes_relations.COMPANION_DEDICATION.EGOISM)

        with self.check_decreased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.COMPANION_DEDICATION, heroes_relations.COMPANION_DEDICATION.NORMAL)

        with self.check_decreased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.COMPANION_DEDICATION, heroes_relations.COMPANION_DEDICATION.ALTRUISM)

    def test_defend_in_battle_probability__companion_dedication(self):
        self.companion_record.dedication = relations.DEDICATION.records[0]
        self.hero.set_companion(self.companion)

        for dedication in relations.DEDICATION.records[1:]:
            with self.check_increased(lambda: self.hero.companion.defend_in_battle_probability):
                self.companion_record.dedication = dedication

    def test_defend_in_battle_probability__coherence(self):
        self.hero.set_companion(self.companion)

        with self.check_increased(lambda: self.hero.companion.defend_in_battle_probability):
            self.hero.companion.coherence = 100

    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage', 3)
    def test_hit(self):
        self.assertEqual(self.companion.hit(), 3)
        self.assertEqual(self.companion.health, self.companion.max_health - 3)
        self.assertFalse(self.companion.is_dead)

    @mock.patch('the_tale.game.heroes.objects.Hero.companion_damage', 10000)
    def test_hit__health_lower_zero(self):
        self.assertEqual(self.companion.hit(), self.companion.max_health)
        self.assertEqual(self.companion.health, 0)
        self.assertTrue(self.companion.is_dead)
