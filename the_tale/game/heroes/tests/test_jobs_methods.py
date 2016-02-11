# coding: utf-8
import random

import mock

from the_tale.common.utils import testcase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.artifacts.prototypes import ArtifactRecordPrototype
from the_tale.game.artifacts.storage import artifacts_storage
from the_tale.game.artifacts import relations as artifacts_relations

from the_tale.game.balance import constants as c
from the_tale.game.balance.power import Power
from the_tale.game.logic_storage import LogicStorage

from the_tale.game import relations as game_relations

from the_tale.game.places import storage as places_storage
from the_tale.game.persons import storage as persons_storage

from the_tale.game.heroes import relations

from .. import logic


class JobsMethodsTests(testcase.TestCase):

    def setUp(self):
        super(JobsMethodsTests, self).setUp()

        create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.place = places_storage.places.all()[0]
        self.person = self.place.persons[0]


    def check_job_message(self, place_id, person_id):
        with self.check_delta(lambda: len(self.hero.diary), 1):
            self.hero.job_message(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_money_positive_enemies', job_power=None)


    def check_job_money(self, place_id, person_id):
        old_money = self.hero.money

        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_increased(lambda: self.hero.statistics.money_earned_from_masters):
                self.hero.job_money(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_money_positive_enemies', job_power=1)

        middle_money = self.hero.money

        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_increased(lambda: self.hero.statistics.money_earned_from_masters):
                self.hero.job_money(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_money_positive_enemies', job_power=2)

        self.assertTrue(middle_money - old_money < self.hero.money - middle_money)


    def check_job_artifact(self, place_id, person_id):
        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_delta(lambda: self.hero.bag.occupation, 1):
                with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
                    self.hero.job_artifact(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_artifact_positive_enemies', job_power=1)

        rating = self.hero.bag.values()[0].preference_rating(self.hero.preferences.archetype.power_distribution)
        self.hero.bag.drop_cheapest_item(self.hero.preferences.archetype.power_distribution)

        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_delta(lambda: self.hero.bag.occupation, 1):
                with self.check_delta(lambda: self.hero.statistics.artifacts_had, 1):
                    self.hero.job_artifact(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_artifact_positive_enemies', job_power=2)

        self.assertTrue(rating, self.hero.bag.values()[0].preference_rating(self.hero.preferences.archetype.power_distribution))


    def check_job_experience(self, place_id, person_id):
        self.hero.level = 100

        old_experience = self.hero.experience

        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_increased(lambda: self.hero.experience):
                self.hero.job_experience(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_experience_positive_enemies', job_power=1)

        middle_experience = self.hero.experience

        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_increased(lambda: self.hero.experience):
                self.hero.job_experience(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_experience_positive_enemies', job_power=2)

        self.assertTrue(middle_experience - old_experience < self.hero.experience - middle_experience)


    def check_job_energy(self, place_id, person_id):
        old_energy = self.hero.energy_bonus

        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_increased(lambda: self.hero.energy_bonus):
                self.hero.job_energy(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_energy_positive_enemies', job_power=1)

        middle_energy = self.hero.energy_bonus

        with self.check_delta(lambda: len(self.hero.diary), 1):
            with self.check_increased(lambda: self.hero.energy_bonus):
                self.hero.job_energy(place_id=place_id, person_id=person_id, message_type='job_diary_person_hero_energy_positive_enemies', job_power=2)

        self.assertTrue(middle_energy - old_energy < self.hero.energy_bonus - middle_energy)


    def test_job_message(self):
        self.check_job_message(place_id=self.place.id, person_id=self.person.id)
        self.check_job_message(place_id=self.place.id, person_id=None)

    def test_job_money(self):
        self.check_job_money(place_id=self.place.id, person_id=self.person.id)
        self.check_job_money(place_id=self.place.id, person_id=None)

    def test_job_artifact(self):
        self.check_job_artifact(place_id=self.place.id, person_id=self.person.id)
        self.check_job_artifact(place_id=self.place.id, person_id=None)

    def test_job_experience(self):
        self.check_job_experience(place_id=self.place.id, person_id=self.person.id)
        self.check_job_experience(place_id=self.place.id, person_id=None)

    def test_job_energy(self):
        self.check_job_energy(place_id=self.place.id, person_id=self.person.id)
        self.check_job_energy(place_id=self.place.id, person_id=None)
