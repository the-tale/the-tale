
import smart_imports

smart_imports.all()


class TestRequests(utils_testcase.TestCase):

    def setUp(self):
        super(TestRequests, self).setUp()
        game_logic.create_test_map()

    def test_index(self):
        self.check_redirect(utils_urls.url('guide:'), utils_urls.url('guide:game'))

    def test_registration(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:registration')))

    def test_account_types(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:account-types')))

    def test_behavior_rules(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:behavior-rules')))

    def test_user_agreement(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:user-agreement')))

    def test_payments(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:payments')))

    def test_game(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:game')))

    def test_keepers(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:keepers')))

    def test_persons(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:persons')))

    def test_cities(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:cities')))

    def test_cards(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:cards:')))

    def test_companions(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:companions:')))

    def test_map(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:map')))

    def test_politics(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:politics')))

    def test_hero_abilities(self):
        for ability_type in [None] + list(heroes_abilities_relations.ABILITY_TYPE.records):
            for activation_type in [None] + list(heroes_abilities_relations.ABILITY_ACTIVATION_TYPE.records):
                for availability in heroes_abilities_relations.ABILITY_AVAILABILITY.records:
                    args = {'availability': availability.value}
                    if ability_type is not None:
                        args['ability_type'] = ability_type.value
                    if activation_type is not None:
                        args['activation_type'] = activation_type.value
                    self.check_html_ok(self.request_html(utils_urls.url('guide:hero-abilities', **args)),
                                       texts=(('guide.hero_abilities.activation_type.wrong_format', 0),
                                              ('guide.hero_abilities.ability_type.wrong_format', 0),
                                              ('guide.hero_abilities.availability.wrong_format', 0),))

    def test_hero_preferences(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:hero-preferences')))

    def test_pvp(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:pvp')))

    def test_api(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:api')))

    def test_referrals__unlogined(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:referrals')))

    def test_referrals__logined(self):
        account = self.accounts_factory.create_account()
        self.request_login(account.email)
        self.check_html_ok(self.client.get(utils_urls.url('guide:referrals')))

    def test_zpg(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:zpg')))

    def test_hero_habits(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:hero-habits')))

    def test_press_kit(self):
        self.check_html_ok(self.client.get(utils_urls.url('guide:press-kit')))

    def test_hero_habit_info(self):
        for habit in game_relations.HABIT_TYPE.records:
            self.check_html_ok(self.client.get(utils_urls.url('guide:hero-habit-info', habit=habit.value)))

    def test_world(self):
        self.check_html_ok(self.request_html(utils_urls.url('guide:world')))

    def test_how_to_help(self):
        self.check_html_ok(self.request_html(utils_urls.url('guide:how-to-help')))

    def test_game_resources(self):
        self.check_html_ok(self.request_html(utils_urls.url('guide:game-resources')))

    def test_movement(self):
        self.check_html_ok(self.request_html(utils_urls.url('guide:movement')))

    def test_clans(self):
        self.check_html_ok(self.request_html(utils_urls.url('guide:clans')))

    def test_emissaries(self):
        self.check_html_ok(self.request_html(utils_urls.url('guide:emissaries')))

    def test_creativity_recomendations(self):
        self.check_html_ok(self.request_html(utils_urls.url('guide:creativity-recommendations')))
