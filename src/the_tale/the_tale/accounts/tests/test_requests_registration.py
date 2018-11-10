
import smart_imports

smart_imports.all()


class RequestsRegistrationTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()
        self.url = logic.register_url()

        self.arguments = {'gender': game_relations.GENDER.random(),
                          'race': game_relations.RACE.random(),
                          'archetype': game_relations.ARCHETYPE.random(),
                          'upbringing': tt_beings_relations.UPBRINGING.random(),
                          'first_death': tt_beings_relations.FIRST_DEATH.random(),
                          'age': tt_beings_relations.AGE.random(),
                          'honor': random.choice((game_relations.HABIT_HONOR_INTERVAL.LEFT_1,
                                                  game_relations.HABIT_HONOR_INTERVAL.RIGHT_1)),
                          'peacefulness': random.choice((game_relations.HABIT_PEACEFULNESS_INTERVAL.LEFT_1,
                                                         game_relations.HABIT_PEACEFULNESS_INTERVAL.RIGHT_1)),
                          'name': 'ааа,ббб,ввв,ггг,ддд,еее'}

        self.raw_arguments = {key: value.value if key != 'name' else value
                              for key, value in self.arguments.items()}

    def check_logined(self):
        self.check_html_ok(self.request_html(dext_urls.url('accounts:profile:show')))

    def last_account(self):
        return models.Account.objects.order_by('-created_at')[0]

    @mock.patch('the_tale.game.logic.generate_history', mock.Mock(return_value=['some', None, 'history']))
    def test_registration(self):
        with self.check_delta(models.Account.objects.count, 1), \
             mock.patch.object(amqp_environment.environment.workers.supervisor, 'cmd_register_new_account') as cmd_register_new_account:
            self.check_ajax_ok(self.post_ajax_json(self.url, data=self.raw_arguments))

        self.check_logined()

        account = self.last_account()

        self.assertTrue(account.is_fast)

        self.assertEqual(cmd_register_new_account.call_args_list,
                         [mock.call(account_id=account.id)])

        hero = heroes_logic.load_hero(account.id)

        self.assertEqual(hero.race, self.arguments['race'])
        self.assertEqual(hero.gender, self.arguments['gender'])
        self.assertEqual(','.join(hero.utg_name.forms[:6]), self.arguments['name'])
        self.assertEqual(hero.habit_peacefulness.raw_value, self.arguments['peacefulness'].direction * c.HABITS_NEW_HERO_POINTS)
        self.assertEqual(hero.habit_honor.raw_value, self.arguments['honor'].direction * c.HABITS_NEW_HERO_POINTS)
        self.assertEqual(hero.preferences.archetype, self.arguments['archetype'])
        self.assertEqual(hero.upbringing, self.arguments['upbringing'])
        self.assertEqual(hero.first_death, self.arguments['first_death'])
        self.assertEqual(hero.death_age, self.arguments['age'])

        self.assertEqual(heroes_logic.get_hero_description(hero.id), '[rl]some\n\n[rl]history')

    def test_registration_for_logged_in_user(self):
        account = self.accounts_factory.create_account()

        self.request_login(account.email)

        with self.check_not_changed(models.Account.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.url, data=self.raw_arguments),
                                  'accounts.registration.register.already_registered')

    def test_registration_processing__referer(self):
        referer = 'https://example.com/forum/post/1/'

        with self.check_delta(models.Account.objects.count, 1):
            self.check_ajax_ok(self.client.post(self.url, data=self.raw_arguments, HTTP_REFERER=referer))

        self.assertEqual(self.last_account().referer, referer)

    def test_registration_processing__referral(self):
        owner = self.accounts_factory.create_account()

        with self.check_delta(models.Account.objects.count, 1):
            url = '{}&{}={}'.format(self.url,
                                    conf.settings.REFERRAL_URL_ARGUMENT,
                                    owner.id)
            self.check_ajax_ok(self.post_ajax_json(url, data=self.raw_arguments))

        referral = self.last_account()

        self.assertEqual(referral.referral_of_id, owner.id)
        self.assertEqual(referral.referrals_number, 0)

        owner = models.Account.objects.get(id=owner.id)

        self.assertEqual(owner.referral_of, None)
        self.assertEqual(owner.referrals_number, 0)  # update only on completed registration

    def test_registration_processing__action(self):
        action = 'some_action'

        with self.check_delta(models.Account.objects.count, 1):
            url = '{}&{}={}'.format(self.url,
                                    conf.settings.ACTION_URL_ARGUMENT,
                                    action)
            self.check_ajax_ok(self.post_ajax_json(url, data=self.raw_arguments))

        self.assertEqual(self.last_account().action_id, action)


class CreateHeroTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        game_logic.create_test_map()

        self.url = dext_urls.url('accounts:registration:create-hero')

    def test_authenticated(self):
        account = self.accounts_factory.create_account()
        self.request_login(account.email)

        self.check_redirect(self.url, dext_urls.url('game:'))

    def test_not_authenticated(self):
        self.check_html_ok(self.request_html(self.url))
