# coding: utf-8


from dext.common.utils.urls import url

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map

from the_tale.game.relations import HABIT_TYPE


class TestRequests(TestCase):

    def setUp(self):
        super(TestRequests, self).setUp()
        create_test_map()

    def test_index(self):
        self.check_redirect(url('guide:'), url('guide:game'))

    def test_registration(self):
        self.check_html_ok(self.client.get(url('guide:registration')))

    def test_account_types(self):
        self.check_html_ok(self.client.get(url('guide:account-types')))

    def test_behavior_rules(self):
        self.check_html_ok(self.client.get(url('guide:behavior-rules')))

    def test_user_agreement(self):
        self.check_html_ok(self.client.get(url('guide:user-agreement')))

    def test_payments(self):
        self.check_html_ok(self.client.get(url('guide:payments')))

    def test_game(self):
        self.check_html_ok(self.client.get(url('guide:game')))

    def test_keepers(self):
        self.check_html_ok(self.client.get(url('guide:keepers')))

    def test_persons(self):
        self.check_html_ok(self.client.get(url('guide:persons')))

    def test_cities(self):
        self.check_html_ok(self.client.get(url('guide:cities')))

    def test_cards(self):
        self.check_html_ok(self.client.get(url('guide:cards:')))

    def test_map(self):
        self.check_html_ok(self.client.get(url('guide:map')))

    def test_politics(self):
        self.check_html_ok(self.client.get(url('guide:politics')))

    def test_hero_abilities(self):
        from the_tale.game.heroes.habilities import ABILITY_TYPE, ABILITY_ACTIVATION_TYPE, ABILITY_AVAILABILITY

        for ability_type in [None] + list(ABILITY_TYPE.records):
            for activation_type in [None] + list(ABILITY_ACTIVATION_TYPE.records):
                for availability in ABILITY_AVAILABILITY.records:
                    args = {'availability': availability.value}
                    if ability_type is not None:
                        args['ability_type'] = ability_type.value
                    if activation_type is not None:
                        args['activation_type'] = activation_type.value
                    self.check_html_ok(self.request_html(url('guide:hero-abilities', **args)),
                                       texts=(('guide.hero_abilities.activation_type.wrong_format', 0),
                                              ('guide.hero_abilities.ability_type.wrong_format', 0),
                                              ('guide.hero_abilities.availability.wrong_format', 0),))

    def test_hero_preferences(self):
        self.check_html_ok(self.client.get(url('guide:hero-preferences')))

    def test_pvp(self):
        self.check_html_ok(self.client.get(url('guide:pvp')))

    def test_api(self):
        self.check_html_ok(self.client.get(url('guide:api')))

    def test_referrals__unlogined(self):
        self.check_html_ok(self.client.get(url('guide:referrals')))

    def test_referrals__logined(self):
        register_user('test_user', 'test_user@test.com', '111111')
        self.request_login('test_user@test.com')
        self.check_html_ok(self.client.get(url('guide:referrals')))

    def test_zpg(self):
        self.check_html_ok(self.client.get(url('guide:zpg')))

    def test_hero_habits(self):
        self.check_html_ok(self.client.get(url('guide:hero-habits')))

    def test_press_kit(self):
        self.check_html_ok(self.client.get(url('guide:press-kit')))

    def test_hero_habit_info(self):
        for habit in HABIT_TYPE.records:
            self.check_html_ok(self.client.get(url('guide:hero-habit-info', habit=habit.value)))

    def test_intro_comix(self):
        self.check_html_ok(self.request_html(url('guide:intro-comix')))

    def test_game_resources(self):
        self.check_html_ok(self.request_html(url('guide:game-resources')))
