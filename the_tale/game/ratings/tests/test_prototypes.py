# coding: utf-8

from the_tale.common.utils.testcase import TestCase

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.logic import register_user

from the_tale.game.logic import create_test_map
from the_tale.game import names


from the_tale.game.ratings.models import RatingValues
from the_tale.game.ratings.prototypes import RatingValuesPrototype

from the_tale.linguistics.prototypes import ContributionPrototype
from the_tale.linguistics import relations as linguistics_relations

from the_tale.game.heroes.conf import heroes_settings
from the_tale.game.heroes import models as heroes_models


class PrototypeTestsBase(TestCase):

    def setUp(self):
        super(PrototypeTestsBase, self).setUp()
        self.place1, self.place2, self.place3 = create_test_map()

        register_user('user_1', 'user_1@test.com', '111111')
        register_user('user_2', 'user_2@test.com', '111111')
        register_user('user_3', 'user_3@test.com', '111111')
        register_user('user_4', 'user_4@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_nick('user_1')
        self.account_2 = AccountPrototype.get_by_nick('user_2')
        self.account_3 = AccountPrototype.get_by_nick('user_3')
        self.account_4 = AccountPrototype.get_by_nick('user_4')

class RatingPrototypeTests(PrototypeTestsBase):

    def setUp(self):
        super(RatingPrototypeTests, self).setUp()


    def test_initialize(self):
        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.account_id for rv in RatingValues.objects.all().order_by('account__id')],
                         [self.account_1.id, self.account_2.id, self.account_3.id, self.account_4.id, ])

    def test_fast_accounts_filtration(self):
        register_user('user_5')
        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.account_id for rv in RatingValues.objects.all().order_by('account__id')],
                         [self.account_1.id, self.account_2.id, self.account_3.id, self.account_4.id, ])

    def test_banned_accounts_filtration(self):
        register_user('user_5', 'user_5@test.com', '111111')
        account_5 = AccountPrototype.get_by_nick('user_5')

        account_5.ban_game(1)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.account_id for rv in RatingValues.objects.all().order_by('account__id')],
                         [self.account_1.id, self.account_2.id, self.account_3.id, self.account_4.id, ])

    def set_values(self, account, might=0, level=0, magic_power=0, physic_power=0,
                   pvp_battles_1x1_number=0, pvp_battles_1x1_victories=0, help_count=0, gifts_returned=0, politics_power=0):
        hero = heroes_models.Hero.objects.get(account_id=account.id)
        hero.might = might
        hero.level = level
        hero.raw_power_physic = physic_power
        hero.raw_power_magic = magic_power
        hero.stat_pvp_battles_1x1_number = pvp_battles_1x1_number
        hero.stat_pvp_battles_1x1_victories = pvp_battles_1x1_victories
        hero.stat_help_count = help_count
        hero.stat_gifts_returned = gifts_returned
        hero.stat_politics_multiplier = politics_power
        hero.save()

    def test_might(self):
        self.set_values(self.account_1, might=10)
        self.set_values(self.account_2, might=1)
        self.set_values(self.account_3, might=17)
        self.set_values(self.account_4, might=5)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.might for rv in RatingValues.objects.all().order_by('account__id')],
                         [10.0, 1.0, 17.0, 5.0 ])

    def test_help_count(self):
        self.set_values(self.account_1, help_count=10)
        self.set_values(self.account_2, help_count=1)
        self.set_values(self.account_3, help_count=17)
        self.set_values(self.account_4, help_count=5)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.help_count for rv in RatingValues.objects.all().order_by('account__id')],
                         [10, 1, 17, 5 ])

    def create_bill(self, index, owner, state):
        from the_tale.game.bills.bills import PlaceRenaming
        from the_tale.game.bills.prototypes import BillPrototype

        bill_data = PlaceRenaming(place_id=self.place1.id, name_forms=names.generator.get_test_name('new_name_%d' % index))
        bill = BillPrototype.create(owner, 'bill-%d-caption' % index, 'bill-%d-rationale' % index, bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = state
        bill.save()


    def test_bills_count(self):
        from the_tale.forum.models import Category, SubCategory
        from the_tale.game.bills.conf import bills_settings
        from the_tale.game.bills import relations as bills_relations

        forum_category = Category.objects.create(caption='category-1', slug='category-1')
        SubCategory.objects.create(caption=bills_settings.FORUM_CATEGORY_UID + '-caption',
                                   uid=bills_settings.FORUM_CATEGORY_UID,
                                   category=forum_category)

        self.create_bill(0, self.account_2, bills_relations.BILL_STATE.VOTING)
        self.create_bill(1, self.account_2, bills_relations.BILL_STATE.ACCEPTED)
        self.create_bill(2, self.account_2, bills_relations.BILL_STATE.REJECTED)

        self.create_bill(3, self.account_3, bills_relations.BILL_STATE.ACCEPTED)
        self.create_bill(4, self.account_3, bills_relations.BILL_STATE.ACCEPTED)
        self.create_bill(5, self.account_3, bills_relations.BILL_STATE.REJECTED)

        self.create_bill(6, self.account_1, bills_relations.BILL_STATE.REJECTED)
        self.create_bill(7, self.account_1, bills_relations.BILL_STATE.REJECTED)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.bills_count for rv in RatingValues.objects.all().order_by('account__id')],
                         [0, 1, 2, 0])

    def create_linguistic_contribution(self, account, type, entity_id):
        ContributionPrototype.create(account_id=account.id,
                                     type=type,
                                     entity_id=entity_id,
                                     source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER,
                                     state=linguistics_relations.CONTRIBUTION_STATE.IN_GAME)

    def test_phrases_count(self):
        self.create_linguistic_contribution(account=self.account_1, type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, entity_id=1)
        self.create_linguistic_contribution(account=self.account_1, type=linguistics_relations.CONTRIBUTION_TYPE.WORD, entity_id=1)
        self.create_linguistic_contribution(account=self.account_1, type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, entity_id=2)
        self.create_linguistic_contribution(account=self.account_3, type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, entity_id=2)
        self.create_linguistic_contribution(account=self.account_3, type=linguistics_relations.CONTRIBUTION_TYPE.WORD, entity_id=2)
        self.create_linguistic_contribution(account=self.account_2, type=linguistics_relations.CONTRIBUTION_TYPE.WORD, entity_id=3)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.phrases_count for rv in RatingValues.objects.all().order_by('account__id')],
                         [2, 0, 1, 0])


    def test_level(self):
        self.set_values(self.account_1, level=10)
        self.set_values(self.account_2, level=9)
        self.set_values(self.account_3, level=7)
        self.set_values(self.account_4, level=1)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.level for rv in RatingValues.objects.all().order_by('account__id')],
                         [10, 9, 7, 1 ])


    def test_magic_power(self):
        self.set_values(self.account_1, magic_power=9)
        self.set_values(self.account_2, magic_power=10)
        self.set_values(self.account_3, magic_power=7)
        self.set_values(self.account_4, magic_power=1)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.magic_power for rv in RatingValues.objects.all().order_by('account__id')],
                         [9, 10, 7, 1 ])

    def test_physic_power(self):
        self.set_values(self.account_1, physic_power=9)
        self.set_values(self.account_2, physic_power=10)
        self.set_values(self.account_3, physic_power=7)
        self.set_values(self.account_4, physic_power=1)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.physic_power for rv in RatingValues.objects.all().order_by('account__id')],
                         [9, 10, 7, 1 ])


    def test_pvp(self):
        self.set_values(self.account_1, pvp_battles_1x1_number=0, pvp_battles_1x1_victories=0)
        self.set_values(self.account_2, pvp_battles_1x1_number=5, pvp_battles_1x1_victories=1)
        self.set_values(self.account_3, pvp_battles_1x1_number=100, pvp_battles_1x1_victories=2)
        self.set_values(self.account_4, pvp_battles_1x1_number=200, pvp_battles_1x1_victories=3)

        RatingValuesPrototype.recalculate()

        self.assertEqual(heroes_settings.MIN_PVP_BATTLES, 25)

        self.assertEqual([rv.pvp_battles_1x1_number for rv in RatingValues.objects.all().order_by('account__id')],
                         [0, 5, 100, 200 ])

        self.assertEqual([rv.pvp_battles_1x1_victories for rv in RatingValues.objects.all().order_by('account__id')],
                         [0, 0.0, 0.02, 0.015])


    def test_gifts_returned(self):
        self.set_values(self.account_1, gifts_returned=9)
        self.set_values(self.account_2, gifts_returned=10)
        self.set_values(self.account_3, gifts_returned=7)
        self.set_values(self.account_4, gifts_returned=1)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.gifts_returned for rv in RatingValues.objects.all().order_by('account__id')],
                         [9, 10, 7, 1 ])


    def test_politics_power(self):
        self.set_values(self.account_1, politics_power=9)
        self.set_values(self.account_2, politics_power=10)
        self.set_values(self.account_3, politics_power=7)
        self.set_values(self.account_4, politics_power=1)

        RatingValuesPrototype.recalculate()
        self.assertEqual([rv.politics_power for rv in RatingValues.objects.all().order_by('account__id')],
                         [9, 10, 7, 1 ])
