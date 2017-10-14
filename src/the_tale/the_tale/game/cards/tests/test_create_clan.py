from unittest import mock

from the_tale.amqp_environment import environment

from the_tale.common.utils import testcase

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts.clans import models as clans_models
from the_tale.accounts.clans import prototypes as clans_prototypes
from the_tale.accounts.clans.conf import clans_settings

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.logic import create_test_map

from the_tale.game import names

from the_tale.game.cards import cards
from the_tale.game.cards.tests.helpers import CardsTestMixin

from the_tale.game.postponed_tasks import ComplexChangeTask
from the_tale.game.balance import constants as c

from the_tale.forum.prototypes import CategoryPrototype


class CreateClanTests(CardsTestMixin, testcase.TestCase):
    CARD = cards.CARD.CREATE_CLAN

    def setUp(self):
        super(CreateClanTests, self).setUp()

        CategoryPrototype.create(caption='category-1', slug=clans_settings.FORUM_CATEGORY_SLUG, order=0)

        self.place_1, self.place_2, self.place_3 = create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)

        self.hero = self.storage.accounts_to_heroes[self.account_1.id]

        environment.deinitialize()
        environment.initialize()


    def test_use(self):

        self.assertEqual(clans_models.Clan.objects.count(), 0)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.SUCCESSED, ComplexChangeTask.STEP.SUCCESS, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        clan = clans_models.Clan.objects.all()[0]

        self.assertEqual(clan.name, 'xxx')
        self.assertEqual(clan.abbr, 'yyy')

        membership = clans_models.Membership.objects.all()[0]

        self.assertEqual(membership.clan.id, clan.id)
        self.assertEqual(membership.account.id, self.account_1.id)
        self.assertTrue(membership.role.is_LEADER)


    def test_already_in_clan(self):
        clans_prototypes.ClanPrototype.create(owner=self.account_1,
                                              abbr='aaa',
                                              name='bbb',
                                              motto='Veni, vidi, vici!',
                                              description='')

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)


    def test_name_exists(self):
        clans_prototypes.ClanPrototype.create(owner=self.account_2,
                                              abbr='aaa',
                                              name='xxx',
                                              motto='Veni, vidi, vici!',
                                              description='')

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)


    def test_abbr_exists(self):
        clans_prototypes.ClanPrototype.create(owner=self.account_2,
                                              abbr='yyy',
                                              name='bbb',
                                              motto='Veni, vidi, vici!',
                                              description='')

        self.assertEqual(clans_models.Clan.objects.count(), 1)

        result, step, postsave_actions = self.CARD.effect.use(**self.use_attributes(hero=self.hero, storage=self.storage, extra_data={'name': 'xxx', 'abbr': 'yyy'}))

        self.assertEqual((result, step, postsave_actions), (ComplexChangeTask.RESULT.FAILED, ComplexChangeTask.STEP.ERROR, ()))

        self.assertEqual(clans_models.Clan.objects.count(), 1)
