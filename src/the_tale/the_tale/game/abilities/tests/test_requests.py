
import smart_imports

smart_imports.all()


class AbilityRequests(utils_testcase.TestCase):

    def setUp(self):
        super(AbilityRequests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

    def test_activate_ability_unlogined(self):
        self.check_ajax_error(self.client.post(logic.use_ability_url(relations.ABILITY_TYPE.HELP)), 'common.login_required')

    def test_activate_ability(self):
        self.request_login(self.account.email)
        response = self.client.post(logic.use_ability_url(relations.ABILITY_TYPE.HELP))
        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)

    @mock.patch('the_tale.game.abilities.relations.ABILITY_TYPE.HELP.cost', 100500)
    def test_activate_ability__no_energy(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.client.post(logic.use_ability_url(relations.ABILITY_TYPE.HELP)), 'game.abilities.use.no_enough_energy')
        self.assertEqual(PostponedTaskPrototype._db_count(), 0)
