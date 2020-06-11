
import smart_imports

smart_imports.all()


class JobsMethodsTests(utils_testcase.TestCase):

    def setUp(self):
        super(JobsMethodsTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account.id)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.place = places_storage.places.all()[0]
        self.person = self.place.persons[0]

    def check_job_message(self, place_id, person_id):
        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            self.hero.job_message(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_money_positive_enemies', job_power=None)

    def check_job_money(self, place_id, person_id):
        old_money = self.hero.money

        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            with self.check_delta(lambda: self.hero.statistics.money_earned_from_masters, 777):
                self.hero.job_money(place_id=place_id,
                                    person_id=person_id,
                                    message_type='job_diary_person_hero_money_positive_enemies',
                                    effect_value=777)

        middle_money = self.hero.money

        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            with self.check_delta(lambda: self.hero.statistics.money_earned_from_masters, 100500):
                self.hero.job_money(place_id=place_id,
                                    person_id=person_id,
                                    message_type='job_diary_person_hero_money_positive_enemies',
                                    effect_value=100500)

        self.assertTrue(middle_money - old_money < self.hero.money - middle_money)

    def check_job_artifact(self, place_id, person_id):
        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            with self.check_delta(lambda: self.hero.bag.occupation, 1):
                with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
                    self.hero.job_artifact(place_id=place_id, person_id=person_id,
                                           message_type='job_diary_person_hero_artifact_positive_enemies',
                                           effect_value={artifacts_relations.RARITY.RARE.value: 1,
                                                         artifacts_relations.RARITY.EPIC.value: 0})

        artifact = self.hero.bag.pop_random_artifact()

        self.assertTrue(artifact.rarity.is_RARE)

        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            with self.check_delta(lambda: self.hero.bag.occupation, 1):
                with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
                    self.hero.job_artifact(place_id=place_id,
                                           person_id=person_id,
                                           message_type='job_diary_person_hero_artifact_positive_enemies',
                                           effect_value={artifacts_relations.RARITY.RARE.value: 0,
                                                         artifacts_relations.RARITY.EPIC.value: 1})

        artifact = self.hero.bag.pop_random_artifact()

        self.assertTrue(artifact.rarity.is_EPIC)

    def check_job_experience(self, place_id, person_id):
        self.hero.level = 100

        old_experience = self.hero.experience

        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            with self.check_delta(lambda: self.hero.experience, 777):
                self.hero.job_experience(place_id=place_id,
                                         person_id=person_id,
                                         message_type='job_diary_person_hero_experience_positive_enemies',
                                         effect_value=777)

        middle_experience = self.hero.experience

        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            with self.check_delta(lambda: self.hero.experience, 888):
                self.hero.job_experience(place_id=place_id,
                                         person_id=person_id,
                                         message_type='job_diary_person_hero_experience_positive_enemies',
                                         effect_value=888)

        self.assertTrue(middle_experience - old_experience < self.hero.experience - middle_experience)

    def check_job_cards(self, place_id, person_id):
        cards_tt_services.storage.cmd_debug_clear_service()

        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            self.hero.job_cards(place_id=place_id,
                                person_id=person_id,
                                message_type='job_diary_person_hero_cards_positive_enemies',
                                effect_value=100)

            cards = cards_tt_services.storage.cmd_get_items(self.account.id)

            self.assertEqual(len(cards), 100)

            self.assertFalse(any(card.available_for_auction for card in cards.values()))
            self.assertTrue(all(card.type.availability.is_FOR_ALL for card in cards.values()))

        cards_tt_services.storage.cmd_debug_clear_service()

        self.account.prolong_premium(30)
        self.account.save()

        with self.check_calls_count('the_tale.game.heroes.tt_services.DiaryClient.cmd_push_message', 1):
            self.hero.job_cards(place_id=place_id,
                                person_id=person_id,
                                message_type='job_diary_person_hero_cards_positive_enemies',
                                effect_value=100)

            cards = cards_tt_services.storage.cmd_get_items(self.account.id)

            self.assertEqual(len(cards), 100)

            self.assertTrue(all(card.available_for_auction for card in cards.values()))
            self.assertTrue(any(card.type.availability.is_FOR_PREMIUMS for card in cards.values()))

    def test_job_message(self):
        self.check_job_message(place_id=self.place.id, person_id=self.person.id)

    def test_job_money(self):
        self.check_job_money(place_id=self.place.id, person_id=self.person.id)

    def test_job_artifact(self):
        self.check_job_artifact(place_id=self.place.id, person_id=self.person.id)

    def test_job_experience(self):
        self.check_job_experience(place_id=self.place.id, person_id=self.person.id)

    def test_job_cards(self):
        self.check_job_cards(place_id=self.place.id, person_id=self.person.id)

    def test_job_artifact__better_then_equipped(self):
        self.hero.level = 100

        self.hero.randomize_equip()

        place = places_storage.places.all()[0]

        for i in range(100):
            self.hero.job_artifact(place_id=place.id,
                                   person_id=place.persons[0].id,
                                   message_type='job_diary_person_hero_artifact_positive_enemies',
                                   effect_value={artifacts_relations.RARITY.RARE.value: 0.5,
                                                 artifacts_relations.RARITY.EPIC.value: 0.5})

            artifact = list(self.hero.bag.values())[0]

            power_distribution = self.hero.preferences.archetype.power_distribution

            self.assertTrue(artifact.preference_rating(power_distribution) >
                            self.hero.equipment.get(artifact.type.equipment_slot).preference_rating(power_distribution))

            self.hero.equip_from_bag()

            self.hero.bag.pop_random_artifact()
