
import smart_imports

smart_imports.all()


class ChooseRequestsTests(utils_testcase.TestCase, helpers.QuestTestsMixin):

    def setUp(self):
        super(ChooseRequestsTests, self).setUp()

        game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()

        self.storage = game_logic_storage.LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.choice_uid = '[ns-0]choice_1'
        self.option_uid = '#option<[ns-0]choice_1, [ns-0]choice_2>'

    @mock.patch('questgen.quests.quests_base.QuestsBase._available_quests', lambda *argv, **kwargs: [helpers.QuestWith2ChoicePoints])
    def test_choose_no_account(self):
        self.turn_to_quest(self.storage, self.hero.id)
        response = self.client.post(utils_urls.url('game:quests:api-choose', option_uid=self.option_uid, api_version='1.0', api_client=django_settings.API_CLIENT))
        self.check_ajax_error(response, 'common.login_required')

    @mock.patch('questgen.quests.quests_base.QuestsBase._available_quests', lambda *argv, **kwargs: [helpers.QuestWith2ChoicePoints])
    def test_choose_processing(self):
        self.turn_to_quest(self.storage, self.hero.id)

        self.request_login(self.account.email)
        response = self.client.post(utils_urls.url('game:quests:api-choose', option_uid=self.option_uid, api_version='1.0', api_client=django_settings.API_CLIENT))

        task = PostponedTaskPrototype._db_get_object(0)
        self.check_ajax_processing(response, task.status_url)
        self.assertEqual(PostponedTask.objects.all().count(), 1)
