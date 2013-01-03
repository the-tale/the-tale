# coding: utf-8

from django.test import TestCase

from forum.prototypes import CategoryPrototype, SubCategoryPrototype, ThreadPrototype, PostPrototype
from forum.models import Thread, Post

from accounts.models import Award, AWARD_TYPE
from accounts.logic import register_user
from accounts.prototypes import AccountPrototype

from blogs.prototypes import PostPrototype as BlogPostPrototype, POST_STATE as BLOG_POST_STATE
from blogs.conf import blogs_settings

from game.logic import create_test_map

from game.heroes.prototypes import HeroPrototype

from game.workers.environment import workers_environment
from game.bills.prototypes import BillPrototype, VotePrototype
from game.bills.bills import PlaceRenaming
from game.bills.models import BILL_STATE, Vote
from game.bills.conf import bills_settings

from game.phrase_candidates.prototypes import PhraseCandidatePrototype
from game.phrase_candidates.models import PHRASE_CANDIDATE_STATE

class MightCalculatorTests(TestCase):

    def setUp(self):
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        self.account = AccountPrototype.get_by_id(account_id)
        self.hero = HeroPrototype.get_by_account_id(account_id)

        result, account_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')
        self.account_2 = AccountPrototype.get_by_id(account_id)
        self.hero_2 = HeroPrototype.get_by_account_id(account_id)

        self.forum_category = CategoryPrototype.create('category', 'category-slug', 0)
        self.bills_subcategory = SubCategoryPrototype.create(self.forum_category, 'subcategory', bills_settings.FORUM_CATEGORY_SLUG, 0)
        self.blogs_subcategory = SubCategoryPrototype.create(self.forum_category, blogs_settings.FORUM_CATEGORY_SLUG + '-caption', blogs_settings.FORUM_CATEGORY_SLUG, 1)


    def test_initialize(self):
        self.assertEqual(self.hero.might, 0)

    def test_no_might(self):
        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero), 0)

    def test_forum_thread_might(self):
        ThreadPrototype.create(self.bills_subcategory, 'caption', self.account, 'text')

        self.assertTrue(workers_environment.might_calculator.calculate_might(self.hero) > 0)
        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero_2), 0)

    def test_forum_post_might(self):
        thread = ThreadPrototype.create(self.bills_subcategory, 'caption', self.account_2, 'text')
        PostPrototype.create(thread, self.account, 'text')

        self.assertTrue(workers_environment.might_calculator.calculate_might(self.hero) > 0)
        self.assertTrue(workers_environment.might_calculator.calculate_might(self.hero_2) > 0)

    def test_accepted_bill_might(self):
        old_might = workers_environment.might_calculator.calculate_might(self.hero)
        bill_data = PlaceRenaming(place_id=self.place_1.id, base_name='bill_place')
        bill = BillPrototype.create(self.account, 'caption', 'rationale', bill_data)
        bill.set_state(BILL_STATE.ACCEPTED)
        bill.save()

        Thread.objects.all().delete()
        Post.objects.all().delete()
        Vote.objects.all().delete()

        self.assertTrue(workers_environment.might_calculator.calculate_might(self.hero) > old_might)
        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero_2), 0)

    def test_voted_bill_might(self):
        old_might = workers_environment.might_calculator.calculate_might(self.hero)
        bill_data = PlaceRenaming(place_id=self.place_1.id, base_name='bill_place')
        bill = BillPrototype.create(self.account, 'caption', 'rationale', bill_data)
        bill.set_state(BILL_STATE.VOTING)
        bill.save()

        Thread.objects.all().delete()
        Post.objects.all().delete()
        Vote.objects.all().delete()

        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero), old_might)
        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero_2), 0)

    def test_rejected_bill_might(self):
        old_might = workers_environment.might_calculator.calculate_might(self.hero)
        bill_data = PlaceRenaming(place_id=self.place_1.id, base_name='bill_place')
        bill = BillPrototype.create(self.account, 'caption', 'rationale', bill_data)
        bill.set_state(BILL_STATE.REJECTED)
        bill.save()

        Thread.objects.all().delete()
        Post.objects.all().delete()
        Vote.objects.all().delete()

        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero), old_might)
        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero_2), 0)

    def test_forum_vote_might(self):
        old_might = workers_environment.might_calculator.calculate_might(self.hero)
        bill_data = PlaceRenaming(place_id=self.place_1.id, base_name='bill_place')
        bill = BillPrototype.create(self.account_2, 'caption', 'rationale', bill_data)
        bill.set_state(BILL_STATE.REJECTED)
        bill.save()

        Thread.objects.all().delete()
        Post.objects.all().delete()
        Vote.objects.all().delete()

        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero_2), old_might)
        self.assertEqual(workers_environment.might_calculator.calculate_might(self.hero), 0)

        VotePrototype.create(self.account, bill, False)
        self.assertTrue(workers_environment.might_calculator.calculate_might(self.hero) > 0)

    def test_phrase_candidate_might(self):
        old_might = workers_environment.might_calculator.calculate_might(self.hero)
        phrase =  PhraseCandidatePrototype.create(type_='type',
                                                  type_name=u'type name',
                                                  subtype='subtype',
                                                  subtype_name=u'subtype name',
                                                  author=self.account,
                                                  text=u'text')

        self.assertEqual(old_might, workers_environment.might_calculator.calculate_might(self.hero))
        phrase.state = PHRASE_CANDIDATE_STATE.ADDED
        phrase.save()

        new_might = workers_environment.might_calculator.calculate_might(self.hero)
        self.assertTrue(new_might > old_might)

        phrase =  PhraseCandidatePrototype.create(type_='type',
                                                  type_name=u'type name',
                                                  subtype='subtype',
                                                  subtype_name=u'subtype name',
                                                  author=self.account_2,
                                                  text=u'text')
        phrase.state = PHRASE_CANDIDATE_STATE.ADDED
        phrase.save()

        self.assertEqual(new_might, workers_environment.might_calculator.calculate_might(self.hero))


    def test_folclor_might(self):
        old_might = workers_environment.might_calculator.calculate_might(self.hero)
        post = BlogPostPrototype.create(author=self.account, caption='caption', text='text')

        Thread.objects.all().delete()
        Post.objects.all().delete()
        Vote.objects.all().delete()

        self.assertEqual(old_might, workers_environment.might_calculator.calculate_might(self.hero))

        post.state = BLOG_POST_STATE.ACCEPTED
        post.model.votes = 1
        post.save()

        new_might = workers_environment.might_calculator.calculate_might(self.hero)
        self.assertTrue(new_might > old_might)

        post = BlogPostPrototype.create(author=self.account_2, caption='caption', text='text')

        Thread.objects.all().delete()
        Post.objects.all().delete()
        Vote.objects.all().delete()

        post.state = BLOG_POST_STATE.ACCEPTED
        post.model.votes = 1
        post.save()

        self.assertEqual(new_might, workers_environment.might_calculator.calculate_might(self.hero))


    def test_custom_might(self):
        Award.objects.create(account=self.account.model, type=AWARD_TYPE.BUG_MINOR)
        self.assertTrue(workers_environment.might_calculator.calculate_might(self.hero) > 0)
