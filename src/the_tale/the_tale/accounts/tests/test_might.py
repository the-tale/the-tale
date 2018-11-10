
import smart_imports

smart_imports.all()


class CalculateMightTests(utils_testcase.TestCase):

    def setUp(self):
        super(CalculateMightTests, self).setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account(referral_of_id=self.account.id)

        self.forum_category = forum_prototypes.CategoryPrototype.create('category', 'category-slug', 0)
        self.bills_subcategory = forum_prototypes.SubCategoryPrototype.create(self.forum_category, 'subcategory', order=0, uid=bills_conf.settings.FORUM_CATEGORY_UID)
        self.blogs_subcategory = forum_prototypes.SubCategoryPrototype.create(self.forum_category, blogs_conf.settings.FORUM_CATEGORY_UID + '-caption', order=1, uid=blogs_conf.settings.FORUM_CATEGORY_UID)

        self.restricted_subcategory = forum_prototypes.SubCategoryPrototype.create(self.forum_category,
                                                                                   'restricted-caption',
                                                                                   order=2,
                                                                                   restricted=True,
                                                                                   uid='restricted-sub')
        self.game_subcategory = forum_prototypes.SubCategoryPrototype.create(self.forum_category,
                                                                             'restricted-caption',
                                                                             order=2,
                                                                             restricted=True,
                                                                             uid=portal_conf.settings.FORUM_GAMES_SUBCATEGORY)

    def test_initialize(self):
        self.assertEqual(self.account.might, 0)

    def test_no_might(self):
        self.assertEqual(might.calculate_might(self.account), 0)

    def test_forum_thread_might(self):
        forum_prototypes.ThreadPrototype.create(self.bills_subcategory, 'caption', self.account, 'text')

        self.assertTrue(might.calculate_might(self.account) > 0)
        self.assertEqual(might.calculate_might(self.account_2), 0)

    def test_forum_thread_might__restricted(self):
        forum_prototypes.ThreadPrototype.create(self.restricted_subcategory, 'caption', self.account, 'text')
        self.assertEqual(might.calculate_might(self.account), 0)

    def test_forum_thread_might__game_subcategory(self):
        forum_prototypes.ThreadPrototype.create(self.game_subcategory, 'caption', self.account, 'text')
        self.assertEqual(might.calculate_might(self.account), 0)

    def test_forum_post_might(self):
        thread = forum_prototypes.ThreadPrototype.create(self.bills_subcategory, 'caption', self.account_2, 'text')
        forum_prototypes.PostPrototype.create(thread, self.account, 'text')

        self.assertTrue(might.calculate_might(self.account) > 0)
        self.assertTrue(might.calculate_might(self.account_2) > 0)

    def test_forum_post_might__restricted(self):
        thread = forum_prototypes.ThreadPrototype.create(self.restricted_subcategory, 'caption', self.account_2, 'text')
        forum_prototypes.PostPrototype.create(thread, self.account, 'text')

        self.assertEqual(might.calculate_might(self.account), 0)
        self.assertEqual(might.calculate_might(self.account_2), 0)

    def test_forum_post_might__game_subcategory(self):
        thread = forum_prototypes.ThreadPrototype.create(self.game_subcategory, 'caption', self.account_2, 'text')
        forum_prototypes.PostPrototype.create(thread, self.account, 'text')

        self.assertEqual(might.calculate_might(self.account), 0)
        self.assertEqual(might.calculate_might(self.account_2), 0)

    def test_accepted_bill_might(self):
        old_might = might.calculate_might(self.account)
        bill_data = bills_bills.place_renaming.PlaceRenaming(place_id=self.place_1.id, name_forms=game_names.generator().get_test_name('bill_place'))
        bill = bills_prototypes.BillPrototype.create(self.account, 'caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = bills_relations.BILL_STATE.ACCEPTED
        bill.save()

        forum_models.Post.objects.all().delete()
        forum_models.Thread.objects.all().delete()
        bills_models.Vote.objects.all().delete()

        self.assertTrue(might.calculate_might(self.account) > old_might)
        self.assertEqual(might.calculate_might(self.account_2), 0)

    def test_voted_bill_might(self):
        old_might = might.calculate_might(self.account)
        bill_data = bills_bills.place_renaming.PlaceRenaming(place_id=self.place_1.id, name_forms=game_names.generator().get_test_name('bill_place'))
        bill = bills_prototypes.BillPrototype.create(self.account, 'caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = bills_relations.BILL_STATE.VOTING
        bill.save()

        forum_models.Post.objects.all().delete()
        forum_models.Thread.objects.all().delete()
        bills_models.Vote.objects.all().delete()

        self.assertEqual(might.calculate_might(self.account), old_might)
        self.assertEqual(might.calculate_might(self.account_2), 0)

    def test_rejected_bill_might(self):
        old_might = might.calculate_might(self.account)
        bill_data = bills_bills.place_renaming.PlaceRenaming(place_id=self.place_1.id, name_forms=game_names.generator().get_test_name('bill_place'))
        bill = bills_prototypes.BillPrototype.create(self.account, 'caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = bills_relations.BILL_STATE.REJECTED
        bill.save()

        forum_models.Post.objects.all().delete()
        forum_models.Thread.objects.all().delete()
        bills_models.Vote.objects.all().delete()

        self.assertEqual(might.calculate_might(self.account), old_might)
        self.assertEqual(might.calculate_might(self.account_2), 0)

    def test_forum_vote_might(self):
        old_might = might.calculate_might(self.account)
        bill_data = bills_bills.place_renaming.PlaceRenaming(place_id=self.place_1.id, name_forms=game_names.generator().get_test_name('bill_place'))
        bill = bills_prototypes.BillPrototype.create(self.account_2, 'caption', bill_data, chronicle_on_accepted='chronicle-on-accepted')
        bill.state = bills_relations.BILL_STATE.REJECTED
        bill.save()

        forum_models.Post.objects.all().delete()
        forum_models.Thread.objects.all().delete()
        bills_models.Vote.objects.all().delete()

        self.assertEqual(might.calculate_might(self.account_2), old_might)
        self.assertEqual(might.calculate_might(self.account), 0)

        bills_prototypes.VotePrototype.create(self.account, bill, bills_relations.VOTE_TYPE.FOR)
        self.assertTrue(might.calculate_might(self.account) > 0)

        bills_models.Vote.objects.all().delete()
        bills_prototypes.VotePrototype.create(self.account, bill, bills_relations.VOTE_TYPE.AGAINST)
        self.assertTrue(might.calculate_might(self.account) > 0)

        bills_models.Vote.objects.all().delete()
        bills_prototypes.VotePrototype.create(self.account, bill, bills_relations.VOTE_TYPE.REFRAINED)
        self.assertEqual(might.calculate_might(self.account), 0)

    def contribute_to_word(self, account_id, entity_id, state=linguistics_relations.CONTRIBUTION_STATE.IN_GAME, source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER):
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.WORD, account_id=account_id, entity_id=entity_id,
                                                            source=source,
                                                            state=state)

    def contribute_to_template(self, account_id, entity_id, state=linguistics_relations.CONTRIBUTION_STATE.IN_GAME, source=linguistics_relations.CONTRIBUTION_SOURCE.PLAYER):
        linguistics_prototypes.ContributionPrototype.create(type=linguistics_relations.CONTRIBUTION_TYPE.TEMPLATE, account_id=account_id, entity_id=entity_id,
                                                            source=source,
                                                            state=state)

    def create_author_contrubutors(self, entity_ids, constructor):
        author_account = self.accounts_factory.create_account()

        for i in entity_ids:
            constructor(author_account.id, i)

        return author_account

    def test_might_for_linguistics__words(self):
        account_3 = self.accounts_factory.create_account()

        old_might = might.calculate_might(self.account)

        author_account = self.create_author_contrubutors(range(1, 6), self.contribute_to_word)

        self.contribute_to_word(self.account.id, entity_id=1)

        self.contribute_to_word(self.account.id, entity_id=2)
        self.contribute_to_word(self.account_2.id, entity_id=2)

        self.contribute_to_word(self.account.id, entity_id=3)
        self.contribute_to_word(self.account_2.id, entity_id=3)
        self.contribute_to_word(account_3.id, entity_id=3)

        self.contribute_to_word(self.account_2.id, entity_id=4)
        self.contribute_to_word(account_3.id, entity_id=4)

        self.contribute_to_word(self.account.id, entity_id=5, state=linguistics_relations.CONTRIBUTION_STATE.ON_REVIEW)

        self.assertEqual(might.calculate_might(self.account), old_might + 5.0 + 5.0 / 2 + 5.0 / 3)

        self.assertEqual(might.calculate_might(author_account), old_might + 5.0 * 5)

    def test_might_for_linguistics__templates(self):
        account_3 = self.accounts_factory.create_account()

        old_might = might.calculate_might(self.account)

        author_account = self.create_author_contrubutors(range(1, 6), self.contribute_to_template)

        self.contribute_to_template(self.account.id, entity_id=1)

        self.contribute_to_template(self.account.id, entity_id=2)
        self.contribute_to_template(self.account_2.id, entity_id=2)

        self.contribute_to_template(self.account.id, entity_id=3)
        self.contribute_to_template(self.account_2.id, entity_id=3)
        self.contribute_to_template(account_3.id, entity_id=3)

        self.contribute_to_template(self.account_2.id, entity_id=4)
        self.contribute_to_template(account_3.id, entity_id=4)

        self.contribute_to_template(self.account.id, entity_id=5, state=linguistics_relations.CONTRIBUTION_STATE.ON_REVIEW)

        self.assertEqual(might.calculate_might(self.account), old_might + 15.0 + 15.0 / 2 + 15.0 / 3)

        self.assertEqual(might.calculate_might(author_account), old_might + 15.0 * 5)

    def test_might_for_linguistics__words___different_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = might.calculate_might(self.account)

        self.create_author_contrubutors(range(1, 5), self.contribute_to_template)

        self.contribute_to_word(self.account.id, entity_id=1)

        self.contribute_to_word(self.account.id, entity_id=2)
        self.contribute_to_word(self.account_2.id, entity_id=2, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        self.contribute_to_word(self.account.id, entity_id=3)
        self.contribute_to_word(self.account_2.id, entity_id=3, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_word(account_3.id, entity_id=3)

        self.contribute_to_word(self.account_2.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_word(account_3.id, entity_id=4)

        self.assertEqual(might.calculate_might(self.account), old_might + 5.0 + 5.0 / 1 + 5.0 / 2)

    def test_might_for_linguistics__templaes___different_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = might.calculate_might(self.account)

        self.create_author_contrubutors(range(1, 5), self.contribute_to_template)

        self.contribute_to_template(self.account.id, entity_id=1)

        self.contribute_to_template(self.account.id, entity_id=2)
        self.contribute_to_template(self.account_2.id, entity_id=2, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        self.contribute_to_template(self.account.id, entity_id=3)
        self.contribute_to_template(self.account_2.id, entity_id=3, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_template(account_3.id, entity_id=3)

        self.contribute_to_template(self.account_2.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_template(account_3.id, entity_id=4)

        self.assertEqual(might.calculate_might(self.account), old_might + 15.0 + 15.0 / 1 + 15.0 / 2)

    def test_might_for_linguistics__words___two_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = might.calculate_might(self.account)

        author_account = self.create_author_contrubutors(range(1, 4), self.contribute_to_word)

        self.contribute_to_word(self.account.id, entity_id=1)

        self.contribute_to_word(self.account.id, entity_id=2)
        self.contribute_to_word(self.account_2.id, entity_id=2, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        self.contribute_to_word(self.account.id, entity_id=3)
        self.contribute_to_word(self.account_2.id, entity_id=3, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_word(account_3.id, entity_id=3)

        self.contribute_to_word(author_account.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_word(self.account.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_word(self.account_2.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_word(account_3.id, entity_id=4)

        self.assertEqual(might.calculate_might(self.account), old_might + 5.0 + 5.0 / 1 + 5.0 / 2 + 5.0 / 2)

    def test_might_for_linguistics__templaes___different_sources(self):
        account_3 = self.accounts_factory.create_account()

        old_might = might.calculate_might(self.account)

        author_account = self.create_author_contrubutors(range(1, 5), self.contribute_to_template)

        self.contribute_to_template(self.account.id, entity_id=1)

        self.contribute_to_template(self.account.id, entity_id=2)
        self.contribute_to_template(self.account_2.id, entity_id=2, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)

        self.contribute_to_template(self.account.id, entity_id=3)
        self.contribute_to_template(self.account_2.id, entity_id=3, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_template(account_3.id, entity_id=3)

        self.contribute_to_word(author_account.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_template(self.account.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_template(self.account_2.id, entity_id=4, source=linguistics_relations.CONTRIBUTION_SOURCE.MODERATOR)
        self.contribute_to_template(account_3.id, entity_id=4)

        self.assertEqual(might.calculate_might(self.account), old_might + 15.0 + 15.0 / 1 + 15.0 / 2 + 15.0 / 2)

    def test_folclor_might(self):
        old_might = might.calculate_might(self.account)

        post = blogs_prototypes.PostPrototype.create(author=self.account, caption='caption', text='text')

        forum_models.Post.objects.all().delete()
        forum_models.Thread.objects.all().delete()
        bills_models.Vote.objects.all().delete()

        new_might = might.calculate_might(self.account)

        self.assertTrue(new_might > old_might)

        post = blogs_prototypes.PostPrototype.create(author=self.account_2, caption='caption', text='text')

        forum_models.Post.objects.all().delete()
        # forum_models.Thread.objects.all().delete()
        bills_models.Vote.objects.all().delete()

        post.state = blogs_relations.POST_STATE.ACCEPTED
        post._model.votes = 1
        post.save()

        self.assertEqual(new_might, might.calculate_might(self.account))

    def test_folclor_might__only_text(self):
        self.assertEqual(might.calculate_might(self.account), 0)

        blogs_prototypes.PostPrototype.create(author=self.account, caption='caption', text='text')

        forum_models.Post.objects.all().delete()
        forum_models.Thread.objects.all().delete()
        bills_models.Vote.objects.all().delete()

        calculated_might = might.calculate_might(self.account)

        blogs_prototypes.PostPrototype.create(author=self.account, caption='caption', text='[b]text[/b]')

        self.assertEqual(might.calculate_might(self.account), calculated_might * 2)

    def test_folclor_might__from_characters(self):

        with self.check_delta(lambda: might.calculate_might(self.account), relations.MIGHT_AMOUNT.FOR_MIN_FOLCLOR_POST.amount * (1 + 1.5 + 2.1)):

            blogs_prototypes.PostPrototype.create(author=self.account, caption='caption', text='x' * blogs_conf.settings.MIN_TEXT_LENGTH)
            blogs_prototypes.PostPrototype.create(author=self.account, caption='caption-2', text='y' * blogs_conf.settings.MIN_TEXT_LENGTH * 2)
            blogs_prototypes.PostPrototype.create(author=self.account, caption='caption-3', text='z' * blogs_conf.settings.MIN_TEXT_LENGTH * 4)

            forum_models.Post.objects.all().delete()
            forum_models.Thread.objects.all().delete()
            bills_models.Vote.objects.all().delete()

    def test_custom_might(self):
        models.Award.objects.create(account=self.account._model, type=relations.AWARD_TYPE.BUG_MINOR)
        self.assertTrue(might.calculate_might(self.account) > 0)

    def test_referral_custom_might(self):
        self.account_2.set_might(666)

        self.assertTrue(might.calculate_might(self.account) > 0)


class CalculateMightHelpersTests(utils_testcase.TestCase):

    def setUp(self):
        super(CalculateMightHelpersTests, self).setUp()

    def test_folclor_post_might(self):
        MIN = blogs_conf.settings.MIN_TEXT_LENGTH
        BASE = relations.MIGHT_AMOUNT.FOR_MIN_FOLCLOR_POST.amount

        self.assertEqual(might.folclor_post_might(MIN), BASE)
        self.assertEqual(might.folclor_post_might(MIN * 2), BASE * 1.5)
        self.assertEqual(might.folclor_post_might(MIN * 3), BASE * 2)
        self.assertEqual(might.folclor_post_might(MIN * 4), BASE * 2.1)
        self.assertEqual(might.folclor_post_might(MIN * 10), BASE * 2.7)
