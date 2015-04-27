# coding: utf-8

from the_tale.common.utils import testcase

from the_tale.forum.prototypes import CategoryPrototype, SubCategoryPrototype, ThreadPrototype, PostPrototype
from the_tale.forum.models import Thread, Post

from the_tale.accounts.models import Award
from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts import relations

from the_tale.blogs.prototypes import PostPrototype as BlogPostPrototype, POST_STATE as BLOG_POST_STATE
from the_tale.blogs.conf import blogs_settings

from the_tale.game import names

from the_tale.game.logic import create_test_map

from the_tale.game.bills.prototypes import BillPrototype, VotePrototype
from the_tale.game.bills.bills import PlaceRenaming
from the_tale.game.bills.models import Vote
from the_tale.game.bills.conf import bills_settings
from the_tale.game.bills.relations import BILL_STATE, VOTE_TYPE

from the_tale.accounts.might import calculate_might, folclor_post_might

from the_tale.linguistics import prototypes as linguistics_prototypes
from the_tale.linguistics import relations as linguistics_relations


class CalculateMightTests(testcase.TestCase):

    def setUp(self):
        super(CalculateMightTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111', referral_of_id=self.account.id)
        self.account_2 = AccountPrototype.get_by_id(account_id)

        self.forum_category = CategoryPrototype.create('category', 'category-slug', 0)
        self.bills_subcategory = SubCategoryPrototype.create(self.forum_category, 'subcategory', order=0, uid=bills_settings.FORUM_CATEGORY_UID)
        self.blogs_subcategory = SubCategoryPrototype.create(self.forum_category, blogs_settings.FORUM_CATEGORY_UID + '-caption', order=1, uid=blogs_settings.FORUM_CATEGORY_UID)


    def test_initialize(self):
        self.assertEqual(self.account.might, 0)

    def test_no_might(self):
        self.assertEqual(calculate_might(self.account), 0)

    def test_forum_thread_might(self):
        ThreadPrototype.create(self.bills_subcategory, 'caption', self.account, 'text')

        self.assertTrue(calculate_might(self.account) > 0)
        self.assertEqual(calculate_might(self.account_2), 0)

    def test_forum_post_might(self):
        thread = ThreadPrototype.create(self.bills_subcategory, 'caption', self.account_2, 'text')
        PostPrototype.create(thread, self.account, 'text')

        self.assertTrue(calculate_might(self.account) > 0)
        self.assertTrue(calculate_might(self.account_2) > 0)

    def test_accepted_bill_might(self):
        old_might = calculate_might(self.account)
        bill_data = PlaceRenaming(place_id=self.place_1.id, name_forms=names.generator.get_test_name('bill_place'))
        bill = BillPrototype.create(self.account, 'caption', 'rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = BILL_STATE.ACCEPTED
        bill.save()

        Post.objects.all().delete()
        Thread.objects.all().delete()
        Vote.objects.all().delete()

        self.assertTrue(calculate_might(self.account) > old_might)
        self.assertEqual(calculate_might(self.account_2), 0)

    def test_voted_bill_might(self):
        old_might = calculate_might(self.account)
        bill_data = PlaceRenaming(place_id=self.place_1.id, name_forms=names.generator.get_test_name('bill_place'))
        bill = BillPrototype.create(self.account, 'caption', 'rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = BILL_STATE.VOTING
        bill.save()

        Post.objects.all().delete()
        Thread.objects.all().delete()
        Vote.objects.all().delete()

        self.assertEqual(calculate_might(self.account), old_might)
        self.assertEqual(calculate_might(self.account_2), 0)

    def test_rejected_bill_might(self):
        old_might = calculate_might(self.account)
        bill_data = PlaceRenaming(place_id=self.place_1.id, name_forms=names.generator.get_test_name('bill_place'))
        bill = BillPrototype.create(self.account, 'caption', 'rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = BILL_STATE.REJECTED
        bill.save()

        Post.objects.all().delete()
        Thread.objects.all().delete()
        Vote.objects.all().delete()

        self.assertEqual(calculate_might(self.account), old_might)
        self.assertEqual(calculate_might(self.account_2), 0)

    def test_forum_vote_might(self):
        old_might = calculate_might(self.account)
        bill_data = PlaceRenaming(place_id=self.place_1.id, name_forms=names.generator.get_test_name('bill_place'))
        bill = BillPrototype.create(self.account_2, 'caption', 'rationale', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = BILL_STATE.REJECTED
        bill.save()

        Post.objects.all().delete()
        Thread.objects.all().delete()
        Vote.objects.all().delete()

        self.assertEqual(calculate_might(self.account_2), old_might)
        self.assertEqual(calculate_might(self.account), 0)

        VotePrototype.create(self.account, bill, VOTE_TYPE.FOR)
        self.assertTrue(calculate_might(self.account) > 0)

        Vote.objects.all().delete()
        VotePrototype.create(self.account, bill, VOTE_TYPE.AGAINST)
        self.assertTrue(calculate_might(self.account) > 0)

        Vote.objects.all().delete()
        VotePrototype.create(self.account, bill, VOTE_TYPE.REFRAINED)
        self.assertEqual(calculate_might(self.account), 0)


    def test_might_for_linguistics__words(self):
        account_3 = self.accounts_factory.create_account()

        old_might = calculate_might(self.account)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=1,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=account_3.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=account_3.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        self.assertEqual(calculate_might(self.account), old_might + 5.0 + 5.0 / 2 + 5.0 / 3)


    def test_might_for_linguistics__templates(self):
        account_3 = self.accounts_factory.create_account()

        old_might = calculate_might(self.account)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=1,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=account_3.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=account_3.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        self.assertEqual(calculate_might(self.account), old_might + 15.0 + 15.0 / 2 + 15.0 / 3)

    def test_might_for_linguistics__words___different_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = calculate_might(self.account)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=1,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=account_3.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=account_3.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        self.assertEqual(calculate_might(self.account), old_might + 5.0 + 5.0 / 1 + 5.0 / 2)

    def test_might_for_linguistics__templaes___different_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = calculate_might(self.account)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=1,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=account_3.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=account_3.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        self.assertEqual(calculate_might(self.account), old_might + 15.0 + 15.0 / 1 + 15.0 / 2)


    def test_might_for_linguistics__words___two_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = calculate_might(self.account)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=1,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=account_3.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=self.account_2.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=account_3.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        self.assertEqual(calculate_might(self.account), old_might + 5.0 + 5.0 / 1 + 5.0 / 2 + 5.0 / 2)

    def test_might_for_linguistics__templaes___different_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = calculate_might(self.account)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=1,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=2,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=account_3.id, entity_id=3,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=self.account_2.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=account_3.id, entity_id=4,
                                                            source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER)

        self.assertEqual(calculate_might(self.account), old_might + 15.0 + 15.0 / 1 + 15.0 / 2 + 15.0 / 2)



    def test_folclor_might(self):
        old_might = calculate_might(self.account)

        post = BlogPostPrototype.create(author=self.account, caption='caption', text='text')

        Post.objects.all().delete()
        Thread.objects.all().delete()
        Vote.objects.all().delete()

        new_might = calculate_might(self.account)

        self.assertTrue(new_might > old_might)

        post = BlogPostPrototype.create(author=self.account_2, caption='caption', text='text')

        Post.objects.all().delete()
        Thread.objects.all().delete()
        Vote.objects.all().delete()

        post.state = BLOG_POST_STATE.ACCEPTED
        post._model.votes = 1
        post.save()

        self.assertEqual(new_might, calculate_might(self.account))


    def test_folclor_might__only_text(self):
        self.assertEqual(calculate_might(self.account), 0)

        BlogPostPrototype.create(author=self.account, caption='caption', text='text')

        Post.objects.all().delete()
        Thread.objects.all().delete()
        Vote.objects.all().delete()

        might = calculate_might(self.account)

        BlogPostPrototype.create(author=self.account, caption='caption', text='[b]text[/b]')

        self.assertEqual(calculate_might(self.account), might * 2)



    def test_folclor_might__from_characters(self):

        with self.check_delta(lambda: calculate_might(self.account), relations.MIGHT_AMOUNT.FOR_MIN_FOLCLOR_POST.amount*(1 + 1.5 + 2.1)):

            BlogPostPrototype.create(author=self.account, caption='caption', text='x'*blogs_settings.MIN_TEXT_LENGTH)
            BlogPostPrototype.create(author=self.account, caption='caption-2', text='y'*blogs_settings.MIN_TEXT_LENGTH*2)
            BlogPostPrototype.create(author=self.account, caption='caption-3', text='z'*blogs_settings.MIN_TEXT_LENGTH*4)

            Post.objects.all().delete()
            Thread.objects.all().delete()
            Vote.objects.all().delete()


    def test_custom_might(self):
        Award.objects.create(account=self.account._model, type=relations.AWARD_TYPE.BUG_MINOR)
        self.assertTrue(calculate_might(self.account) > 0)

    def test_referral_custom_might(self):
        self.account_2.set_might(666)

        self.assertTrue(calculate_might(self.account) > 0)



class CalculateMightHelpersTests(testcase.TestCase):

    def setUp(self):
        super(CalculateMightHelpersTests, self).setUp()

    def test_folclor_post_might(self):
        MIN = blogs_settings.MIN_TEXT_LENGTH
        BASE = relations.MIGHT_AMOUNT.FOR_MIN_FOLCLOR_POST.amount

        self.assertEqual(folclor_post_might(MIN), BASE)
        self.assertEqual(folclor_post_might(MIN*2), BASE*1.5)
        self.assertEqual(folclor_post_might(MIN*3), BASE*2)
        self.assertEqual(folclor_post_might(MIN*4), BASE*2.1)
        self.assertEqual(folclor_post_might(MIN*10), BASE*2.7)
