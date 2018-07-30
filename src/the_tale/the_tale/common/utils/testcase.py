
import smart_imports

smart_imports.all()


def setUp(self):

    accounts_tt_services.players_timers.cmd_debug_clear_service()

    dext_settings.settings.refresh(force=True)

    heroes_storage.position_descriptions.clear()

    places_storage.places.clear()
    places_storage.buildings.clear()
    persons_storage.persons.clear()
    persons_storage.social_connections.clear()
    roads_storage.waymarks.clear()
    roads_storage.roads.clear()
    mobs_storage.mobs.clear()
    companions_storage.companions.clear()
    artifacts_storage.artifacts.clear()
    map_storage.map_info.clear()
    places_storage.resource_exchanges.clear()
    collections_storage.collections.clear()
    collections_storage.kits.clear()
    collections_storage.items.clear()
    achievements_storage.achievements.clear()
    linguistics_storage.dictionary.clear()
    linguistics_storage.lexicon.clear()
    linguistics_storage.restrictions.clear()

    game_prototypes.GameState.start()

    for tag_id in blogs_conf.settings.DEFAULT_TAGS:
        blogs_models.Tag.objects.create(id=tag_id, name='{}'.format(tag_id), description='{}'.format(tag_id))


class TestAccountsFactory(object):

    def __init__(self):
        self._next_account_uid = 0

    def get_next_uid(self):
        self._next_account_uid += 1
        return self._next_account_uid

    def create_account(self, is_fast=False, nick=None, email=None, password='111111', is_bot=False, is_superuser=False, referral_of_id=None):

        if is_fast:
            nick = nick or 'fast-user-{}'.format(self.get_next_uid())
            result, account_id, bundle_id = accounts_logic.register_user(nick, is_bot=is_bot, referral_of_id=referral_of_id)
        else:
            nick = nick or 'test-user-%d' % self.get_next_uid()
            email = email or '{}@test.com'.format(nick)
            result, account_id, bundle_id = accounts_logic.register_user(nick, email, password, is_bot=is_bot, referral_of_id=referral_of_id)

        account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

        if is_superuser:
            account._model.is_superuser = True
            account.save()

        return accounts_prototypes.AccountPrototype.get_by_id(account_id)


class TestCaseMixin(object):

    def request_login(self, email, password='111111', remember=False):
        data = {'email': email, 'password': password}
        if remember:
            data['remember'] = 'remember'
        response = self.client.post(dext_urls.url('accounts:auth:api-login', api_version='1.0', api_client='test-1.0'), data)
        self.check_ajax_ok(response)

    def request_logout(self):
        response = self.client.post(dext_urls.url('accounts:auth:api-logout', api_version='1.0', api_client='test-1.0'))
        self.check_ajax_ok(response)

    @decorators.lazy_property
    def accounts_factory(self):
        return TestAccountsFactory()


class TestCase(dext_testcase.TestCase, TestCaseMixin):
    def setUp(self):
        super(TestCase, self).setUp()
        setUp(self)


class TransactionTestCase(dext_testcase.TransactionTestCase, TestCaseMixin):
    def setUp(self):
        super(TransactionTestCase, self).setUp()
        setUp(self)
