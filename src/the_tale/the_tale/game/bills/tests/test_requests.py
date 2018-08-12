
import smart_imports

smart_imports.all()


class BaseTestRequests(utils_testcase.TestCase):

    def setUp(self):
        super(BaseTestRequests, self).setUp()

        self.place1, self.place2, self.place3 = game_logic.create_test_map()

        self.account1 = self.accounts_factory.create_account()
        # self.account1.prolong_premium(30)
        self.account1._model.created_at -= datetime.timedelta(days=conf.settings.MINIMUM_BILL_OWNER_AGE)
        self.account1.save()

        self.account2 = self.accounts_factory.create_account()
        # self.account2.prolong_premium(30)
        self.account2._model.created_at -= datetime.timedelta(days=conf.settings.MINIMUM_BILL_OWNER_AGE)
        self.account2.save()

        self.request_login(self.account1.email)

        forum_category = forum_models.Category.objects.create(caption='Category-1', slug='category-1')
        forum_models.SubCategory.objects.create(caption=conf.settings.FORUM_CATEGORY_UID + '-caption',
                                                uid=conf.settings.FORUM_CATEGORY_UID,
                                                category=forum_category)

        game_tt_services.debug_clear_service()

    def create_bills(self, number, owner, caption_template, bill_data):
        return [prototypes.BillPrototype.create(owner, caption_template % i, bill_data, chronicle_on_accepted='chronicle-on-accepted-%d' % i) for i in range(number)]

    def check_bill_votes(self, bill_id, votes_for, votes_against):
        bill = models.Bill.objects.get(id=bill_id)
        self.assertEqual(bill.votes_for, votes_for)
        self.assertEqual(bill.votes_against, votes_against)

    def check_vote(self, vote, owner, type, bill_id):
        self.assertEqual(vote.owner, owner)
        self.assertEqual(vote.type, type)
        self.assertEqual(vote._model.bill.id, bill_id)


class TestIndexRequests(BaseTestRequests):

    def test_unlogined(self):
        self.request_logout()
        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=(('pgf-unlogined-message', 1),))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=(('pgf-can-not-participate-in-politics', 1),
                                                                                    ('pgf-unlogined-message', 0),))

    def test_no_bills(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=(('pgf-no-bills-message', 1),))

    def test_bill_creation_locked_message(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', bill_data)
        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=(('pgf-active-bills-limit-reached', 1),
                                                                                    ('pgf-create-new-bill-buttons', 0),
                                                                                    ('pgf-can-not-participate-in-politics', 0)))

    def test_bill_creation_unlocked_message(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=(('pgf-active-bills-limit-reached', 0),
                                                                                    ('pgf-create-new-bill-buttons', 1),
                                                                                    ('pgf-can-not-participate-in-politics', 0)))

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test_can_not_participate_in_politics(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=(('pgf-active-bills-limit-reached', 0),
                                                                                    ('pgf-create-new-bill-buttons', 0),
                                                                                    ('pgf-can-not-participate-in-politics', 1)))

    def test_one_page(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(2, self.account1, 'Caption-a1-%d', bill_data)
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(3, self.account2, 'Caption-a2-%d', bill_data)

        texts = [('pgf-no-bills-message', 0),
                 ('Caption-a1-0', 1),
                 ('Caption-a1-1', 1),
                 ('Caption-a2-0', 1),
                 ('Caption-a2-1', 1),
                 ('Caption-a2-2', 1),
                 (self.account1.nick, 3),
                 (self.account2.nick, 3)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=texts)

    def test_removed_bills(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', bill_data)[0].remove(self.account1)

        self.check_html_ok(self.request_html(django_reverse('game:bills:')), texts=(('pgf-no-bills-message', 1),))

    def create_two_pages(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(conf.settings.BILLS_ON_PAGE, self.account1, 'Caption-a1-%d', bill_data)

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(3, self.account2, 'Caption-a2-%d', bill_data)

    def test_two_pages(self):
        self.create_two_pages()

        texts = [('pgf-no-bills-message', 0),
                 ('Caption-a1-0', 1),
                 ('Caption-a1-1', 1),
                 ('Caption-a1-2', 1),
                 ('Caption-a1-3', 0),
                 ('Caption-a2-0', 0),
                 ('Caption-a2-2', 0),
                 (self.account1.nick, 4), (self.account2.email, 0)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + '?page=2'), texts=texts)

    def test_index_redirect_from_large_page(self):
        self.assertRedirects(self.request_html(django_reverse('game:bills:') + '?page=2'),
                             django_reverse('game:bills:') + '?page=1', status_code=302, target_status_code=200)

    def test_filter_by_user_no_bills_message(self):
        self.create_two_pages()

        account4 = self.accounts_factory.create_account()
        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?owner=%d' % account4.id)),
                           texts=[('pgf-no-bills-message', 1)])

    def test_filter_by_user(self):
        self.create_two_pages()

        account_1_texts = [('pgf-no-bills-message', 0),
                           ('Caption-a1-0', 1),
                           ('Caption-a1-1', 1),
                           ('Caption-a1-2', 1),
                           ('Caption-a1-3', 1),
                           ('Caption-a2-0', 0),
                           ('Caption-a2-2', 0),
                           (self.account1.nick, conf.settings.BILLS_ON_PAGE + 2),  # 1 for main menu, 1 for filter text
                           (self.account2.nick, 0)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?owner=%d' % self.account1.id)),
                           texts=account_1_texts)

        account_2_texts = [('pgf-no-bills-message', 0),
                           ('Caption-a1-0', 0),
                           ('Caption-a1-1', 0),
                           ('Caption-a1-2', 0),
                           ('Caption-a1-3', 0),
                           ('Caption-a2-0', 1),
                           ('Caption-a2-2', 1),
                           (self.account1.nick, 1),  # 1 for main menu
                           (self.account2.nick, 3 + 1)]  # 1 for filter text

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?owner=%d' % self.account2.id)),
                           texts=account_2_texts)

    def test_filter_by_state(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        bill_voting, bill_accepted, bill_rejected = self.create_bills(3, self.account1, 'Caption-%d', bill_data)

        bill_accepted.state = relations.BILL_STATE.ACCEPTED
        bill_accepted._model.voting_end_at = datetime.datetime.now()
        bill_accepted.applyed_at_turn = 0
        bill_accepted.save()

        bill_rejected.state = relations.BILL_STATE.REJECTED
        bill_rejected._model.voting_end_at = datetime.datetime.now()
        bill_rejected.applyed_at_turn = 0
        bill_rejected.save()

        def check_state_filter(self, state, voting_number, accepted_number, rejected_number):
            url = django_reverse('game:bills:')
            if state is not None:
                url += ('?state=%d' % state.value)
            self.check_html_ok(self.request_html(url),
                               texts=[('Caption-0', voting_number),
                                      ('Caption-1', accepted_number),
                                      ('Caption-2', rejected_number)])

        check_state_filter(self, relations.BILL_STATE.VOTING, 1, 0, 0)
        check_state_filter(self, relations.BILL_STATE.ACCEPTED, 0, 1, 0)
        check_state_filter(self, relations.BILL_STATE.REJECTED, 0, 0, 1)
        check_state_filter(self, None, 1, 1, 1)

    def test_filter_by_type_no_bills_message(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', bill_data)

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?bill_type=%d' % bills.person_remove.PersonRemove.type.value)),
                           texts=[('pgf-no-bills-message', 1)])

    def test_filter_by_type(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', bill_data)

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?bill_type=%d' % bills.place_renaming.PlaceRenaming.type.value)),
                           texts=[('pgf-no-bills-message', 0),
                                  ('Caption-0', 1),
                                  ('Caption-1', 1),
                                  ('Caption-2', 1)])

    def test_filter_by_place_no_bills_message(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', bill_data)

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?place=%d' % self.place2.id)),
                           texts=[('pgf-no-bills-message', 1)])

    def test_filter_by_place(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-%d', bill_data)

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(3, self.account1, 'Caption-2-%d', bill_data)

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?place=%d' % self.place1.id)),
                           texts=[('pgf-no-bills-message', 0),
                                  ('Caption-0', 1),
                                  ('Caption-1', 1),
                                  ('Caption-2', 1),
                                  ('Caption-2-0', 0),
                                  ('Caption-2-1', 0),
                                  ('Caption-2-2', 0)])

        self.check_html_ok(self.request_html(django_reverse('game:bills:') + ('?place=%d' % self.place2.id)),
                           texts=[('pgf-no-bills-message', 0),
                                  ('Caption-0', 0),
                                  ('Caption-1', 0),
                                  ('Caption-2', 3),
                                  ('Caption-2-0', 1),
                                  ('Caption-2-1', 1),
                                  ('Caption-2-2', 1)])


class TestNewRequests(BaseTestRequests):

    def test_unlogined(self):
        self.request_logout()
        url_ = django_reverse('game:bills:new') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value)
        self.check_redirect(url_, accounts_logic.login_page_url(url_))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:new') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value)), texts=(('common.fast_account', 1),))

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:new') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value)),
                           texts=(('bills.can_not_participate_in_politics', 1),))

    def test__banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:new') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value)),
                           texts=(('common.ban_any', 1),))

    def test_wrong_type(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:new') + '?bill_type=xxx'), texts=(('bills.new.bill_type.wrong_format', 1),))

    def test_bill_not_enabled(self):
        self.assertFalse(relations.BILL_TYPE.PERSON_REMOVE.enabled)
        self.check_html_ok(self.request_html(django_reverse('game:bills:new') + ('?bill_type=%s' % relations.BILL_TYPE.PERSON_REMOVE.value)), texts=['bills.new.bill_type.not_enabled'])

    def test_success(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:new') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value)), texts=[])

    def test_new_place_renaming(self):
        texts = [('>' + place.name + '<', 1) for place in places_storage.places.all()]
        self.check_html_ok(self.request_html(django_reverse('game:bills:new') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value)), texts=texts)


class TestShowRequests(BaseTestRequests):

    def setUp(self):
        super(TestShowRequests, self).setUp()

        self.hero = heroes_logic.load_hero(account_id=self.account2.id)

        places_logic.add_fame(hero_id=self.hero.id, fames=[(self.place1.id, 1000),
                                                           (self.place2.id, 1000),
                                                           (self.place3.id, 1000)])

    def test_unlogined(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        self.request_logout()
        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=(('pgf-unlogined-message', 1),))

    def test_is_fast(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account2, 'Caption-a2-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        self.account1.is_fast = True
        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-participate-in-politics', 1),))

    def test_can_not_participate_in_politics(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(1, self.account2, 'Caption-a1-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-participate-in-politics', 1),))

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_not_participate_in_politics__voted(self):
        # one vote automaticaly created for bill author
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        self.account1.prolong_premium(-100)
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-participate-in-politics', 0),))

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_not_vote(self):
        game_tt_services.debug_clear_service()

        heroes_logic.save_hero(self.hero)

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(1, self.account2, 'Caption-a1-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        self.account1.prolong_premium(30)
        self.account1.save()

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-vote-message', 1),))

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_not_voted(self):
        game_tt_services.debug_clear_service()

        # one vote automaticaly created for bill author
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        self.create_bills(1, self.account1, 'Caption-a1-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=(('pgf-can-not-vote-message', 0),))

    def test_unexsists(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[0])), status_code=404)

    def test_removed(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place1.id, name_forms=game_names.generator().get_test_name('new_name_1'))
        bill = self.create_bills(1, self.account1, 'Caption-a1-%d', bill_data)[0]
        bill.remove(self.account1)
        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=[('bills.removed', 1)])

    def test_show(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        texts = [('Caption-a2-0', 3 + 2),  # 2 from social sharing
                 ('pgf-voting-block', 0),
                 ('pgf-forum-block', 1),
                 ('pgf-bills-results-summary', 1),
                 ('pgf-bills-results-detailed', 0),
                 ('pgf-can-not-vote-message', 0),
                 (self.place2.name, 2)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show__folclor(self):
        blogs_helpers.prepair_forum()

        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', bill_data)
        bill = prototypes.BillPrototype._db_latest()

        blogs_helpers.create_post_for_meta_object(self.account1, 'folclor-1-caption', 'folclor-1-text', meta_relations.Bill.create_from_object(bill))
        blogs_helpers.create_post_for_meta_object(self.account1, 'folclor-2-caption', 'folclor-2-text', meta_relations.Bill.create_from_object(bill))

        texts = ['folclor-1-caption',
                 'folclor-1-text',
                 'folclor-2-caption']

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show__vote_for(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        texts = [('pgf-voted-for-marker', 1),
                 ('pgf-voted-against-marker', 0),
                 ('pgf-voted-refrained-marker', 0),
                 ('pgf-voting-block', 0)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show__vote_against(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        prototypes.VotePrototype._model_class.objects.all().update(type=relations.VOTE_TYPE.AGAINST)

        texts = [('pgf-voted-for-marker', 0),
                 ('pgf-voted-against-marker', 1),
                 ('pgf-voted-refrained-marker', 0),
                 ('pgf-voting-block', 0)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show__vote_refrained(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        prototypes.VotePrototype._model_class.objects.all().update(type=relations.VOTE_TYPE.REFRAINED)

        texts = [('pgf-voted-for-marker', 0),
                 ('pgf-voted-against-marker', 0),
                 ('pgf-voted-refrained-marker', 1),
                 ('pgf-voting-block', 0)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show_when_not_voting_state(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', bill_data)
        bill = models.Bill.objects.all()[0]
        bill.state = relations.BILL_STATE.ACCEPTED
        bill.voting_end_at = datetime.datetime.now()
        bill.applyed_at_turn = 0
        bill.save()

        texts = [('pgf-bills-results-summary', 0),
                 ('pgf-bills-results-detailed', 1)]

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=texts)

    def test_show_after_voting(self):
        bill_data = bills.place_renaming.PlaceRenaming(place_id=self.place2.id, name_forms=game_names.generator().get_test_name('new_name_2'))
        self.create_bills(1, self.account1, 'Caption-a2-%d', bill_data)
        bill = models.Bill.objects.all()[0]

        texts = [('pgf-voting-block', 1),
                 ('test-already-voted-block', 0),
                 (self.place2.name, 2)]

        self.request_logout()
        self.request_login(self.account2.email)

        self.account2.prolong_premium(30)
        self.account2.save()

        self.check_html_ok(self.request_html(django_reverse('game:bills:show', args=[bill.id])), texts=texts)


class TestCreateRequests(BaseTestRequests):

    def get_post_data(self, depends_on_id=None):
        new_name = game_names.generator().get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'depends_on': depends_on_id,
                     'place': self.place1.id})
        return data

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:create'), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:create'), self.get_post_data()), 'common.fast_account')

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test___can_not_participate_in_politics(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:create'), self.get_post_data()), 'bills.can_not_participate_in_politics')

    def test___banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:create'), self.get_post_data()), 'common.ban_any')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:create') + '?bill_type=xxx', self.get_post_data()), 'bills.create.bill_type.wrong_format')

    def test_type_not_enabled(self):
        self.assertFalse(relations.BILL_TYPE.PERSON_REMOVE.enabled)
        self.check_ajax_error(self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % relations.BILL_TYPE.PERSON_REMOVE.value), self.get_post_data()),
                              'bills.create.bill_type.not_enabled')

    def test_success(self):
        response = self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), self.get_post_data())

        bill = prototypes.BillPrototype(models.Bill.objects.all()[0])
        self.assertEqual(bill.caption, 'bill-caption')
        self.assertEqual(bill.data.place.id, self.place1.id)
        self.assertEqual(bill.data.base_name, 'new-name-нс,ед,им')
        self.assertEqual(bill.votes_for, 1)
        self.assertEqual(bill.votes_against, 0)
        self.assertEqual(bill.chronicle_on_accepted, 'chronicle-on-accepted')

        vote = prototypes.VotePrototype(models.Vote.objects.all()[0])
        self.check_vote(vote, self.account1, relations.VOTE_TYPE.FOR, bill.id)

        self.check_ajax_ok(response, data={'next_url': django_reverse('game:bills:show', args=[bill.id])})

    def test_success_second_bill_error(self):
        self.check_ajax_ok(self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), self.get_post_data()))
        self.check_ajax_error(self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), self.get_post_data()),
                              'bills.create.active_bills_limit_reached')
        self.assertEqual(models.Bill.objects.all().count(), 1)

    @mock.patch('the_tale.game.bills.conf.settings.MINIMUM_BILL_OWNER_AGE', conf.settings.MINIMUM_BILL_OWNER_AGE + 1)
    def test_too_young(self):
        with self.check_not_changed(prototypes.BillPrototype._db_count):
            self.check_ajax_error(self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), self.get_post_data()),
                                  'bills.create.too_young_owner')

    def test_success__with_dependency(self):
        self.account1.prolong_premium(30)
        self.account1.save()

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), self.get_post_data())

        base_bill = models.Bill.objects.all().order_by('created_at')[0]

        response = self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), self.get_post_data(depends_on_id=base_bill.id))

        depended_bill = models.Bill.objects.all().order_by('created_at')[1]

        self.assertEqual(depended_bill.depends_on_id, base_bill.id)

        self.check_ajax_ok(response, data={'next_url': django_reverse('game:bills:show', args=[depended_bill.id])})


class TestVoteRequests(BaseTestRequests):

    def setUp(self):
        super(TestVoteRequests, self).setUp()

        self.account2.prolong_premium(30)
        self.account2.save()

        self.hero = heroes_logic.load_hero(account_id=self.account2.id)

        places_logic.add_fame(hero_id=self.hero.id, fames=[(self.place1.id, 1000),
                                                           (self.place2.id, 1000),
                                                           (self.place3.id, 1000)])

        heroes_logic.save_hero(self.hero)

        new_name = game_names.generator().get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), data)
        self.bill = prototypes.BillPrototype(models.Bill.objects.all()[0])

        self.request_logout()
        self.request_login(self.account2.email)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'common.login_required')

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'common.fast_account')
        self.check_bill_votes(self.bill.id, 1, 0)

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'bills.can_not_participate_in_politics')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test___banned(self):
        self.account2.ban_game(30)
        self.account2.save()
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'common.ban_any')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_bill_not_exists(self):
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', 666, type=relations.VOTE_TYPE.FOR.value), {}), 'bills.bill.not_found')

    def test_wrong_value(self):
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type='bla-bla'), {}), 'bills.vote.type.wrong_format')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_bill_accepted(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'bills.voting_state_required')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_bill_rejected(self):
        self.bill.state = relations.BILL_STATE.REJECTED
        self.bill.save()
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'bills.voting_state_required')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_success_for(self):
        self.check_ajax_ok(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}))
        vote = prototypes.VotePrototype(models.Vote.objects.all()[1])
        self.check_vote(vote, self.account2, relations.VOTE_TYPE.FOR, self.bill.id)
        self.check_bill_votes(self.bill.id, 2, 0)

    @mock.patch('the_tale.game.places.objects.Place.is_new', False)
    def test_can_not_vote(self):
        game_tt_services.debug_clear_service()

        heroes_logic.save_hero(self.hero)

        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'bills.vote.can_not_vote')
        self.check_bill_votes(self.bill.id, 1, 0)

    def test_success_agains(self):
        self.check_ajax_ok(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.AGAINST.value), {}))
        vote = prototypes.VotePrototype(models.Vote.objects.all()[1])
        self.check_vote(vote, self.account2, relations.VOTE_TYPE.AGAINST, self.bill.id)
        self.check_bill_votes(self.bill.id, 1, 1)

    def test_already_exists(self):
        self.check_ajax_ok(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}))
        self.check_ajax_error(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}), 'bills.vote.vote_exists')
        self.check_bill_votes(self.bill.id, 2, 0)


class TestEditRequests(BaseTestRequests):

    def setUp(self):
        super(TestEditRequests, self).setUp()

        new_name = game_names.generator().get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), data)
        self.bill = prototypes.BillPrototype(models.Bill.objects.all()[0])

    def test_unlogined(self):
        self.request_logout()
        url = django_reverse('game:bills:edit', args=[self.bill.id])
        self.check_redirect(url, accounts_logic.login_page_url(url))

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=(('common.fast_account', 1),))

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=(('bills.can_not_participate_in_politics', 1),))

    def test___banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=(('common.ban_any', 1),))

    def test_unexsists(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[666])), status_code=404)

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=[('bills.removed', 1)])

    def test_no_permissions(self):
        self.request_logout()
        self.request_login(self.account2.email)
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=(('bills.not_owner', 1),))

    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=(('bills.voting_state_required', 1),))

    def test_success(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=['chronicle-on-accepted'])

    def test_edit_place_renaming(self):
        texts = [('>' + place.name + '<', 1) for place in places_storage.places.all()]
        self.check_html_ok(self.request_html(django_reverse('game:bills:edit', args=[self.bill.id])), texts=texts)


class TestUpdateRequests(BaseTestRequests):

    def setUp(self):
        super(TestUpdateRequests, self).setUp()

        new_name = game_names.generator().get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), data)
        self.bill = prototypes.BillPrototype(models.Bill.objects.all()[0])

    def get_post_data(self, depends_on_id=None):
        new_name = game_names.generator().get_test_name('new-new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'new-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted-2',
                     'depends_on': depends_on_id,
                     'place': self.place2.id})
        return data

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account1.is_fast = True
        self.account1.save()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'common.fast_account')

    @mock.patch('the_tale.game.bills.views.BillResource.can_participate_in_politics', False)
    def test__can_not_participate_in_politics(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'bills.can_not_participate_in_politics')

    def test___banned(self):
        self.account1.ban_game(30)
        self.account1.save()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'common.ban_any')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[666]), self.get_post_data()), 'bills.bill.not_found')

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id])), 'bills.removed')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login(self.account2.email)
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'bills.not_owner')

    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()), 'bills.voting_state_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), {}), 'bills.update.form_errors')

    def test_update_success(self):
        old_updated_at = self.bill.updated_at

        self.assertEqual(forum_models.Post.objects.all().count(), 1)

        self.check_ajax_ok(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data()))

        self.bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertTrue(old_updated_at < self.bill.updated_at)

        self.assertEqual(forum_models.Post.objects.all().count(), 2)

        self.assertEqual(self.bill.chronicle_on_accepted, 'chronicle-on-accepted-2')

        self.bill._model.delete()

    def test_update_success__setup_depends_on(self):

        self.account1.prolong_premium(30)
        self.account1.save()

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), self.get_post_data())

        base_bill_id = models.Bill.objects.all().order_by('created_at')[1].id

        self.assertIsNone(self.bill.depends_on)
        self.assertEqual(forum_models.Post.objects.all().count(), 2)

        self.check_ajax_ok(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data(depends_on_id=base_bill_id)))

        bill = prototypes.BillPrototype.get_by_id(self.bill.id)
        self.assertEqual(bill.depends_on.id, base_bill_id)

        self.assertEqual(forum_models.Post.objects.all().count(), 3)

    def test_update_success__recursive(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:update', args=[self.bill.id]), self.get_post_data(depends_on_id=self.bill.id)),
                              'bills.update.form_errors')


class TestModerationPageRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerationPageRequests, self).setUp()

        new_name = game_names.generator().get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), data)
        self.bill = prototypes.BillPrototype(models.Bill.objects.all()[0])

        self.request_logout()
        self.request_login(self.account2.email)

        group = utils_permissions.sync_group('bills moderators group', ['bills.moderate_bill'])
        group.user_set.add(self.account2._model)

    def test_unlogined(self):
        self.request_logout()
        url = django_reverse('game:bills:moderate', args=[self.bill.id])
        self.check_redirect(url, accounts_logic.login_page_url(url))

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:moderate', args=[self.bill.id])), texts=(('common.fast_account', 1),))

    def test_unexsists(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:moderate', args=[666])), status_code=404)

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_html_ok(self.request_html(django_reverse('game:bills:moderate', args=[self.bill.id])), texts=[('bills.removed', 1)])

    def test_no_permissions(self):
        self.request_logout()
        self.request_login(self.account1.email)
        self.check_html_ok(self.request_html(django_reverse('game:bills:moderate', args=[self.bill.id])), texts=(('bills.moderator_rights_required', 1),))

    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()
        self.check_html_ok(self.request_html(django_reverse('game:bills:moderate', args=[self.bill.id])), texts=(('bills.voting_state_required', 1),))

    def test_success(self):
        self.check_html_ok(self.request_html(django_reverse('game:bills:moderate', args=[self.bill.id])))


class TestModerateRequests(BaseTestRequests):

    def setUp(self):
        super(TestModerateRequests, self).setUp()

        new_name = game_names.generator().get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'place': self.place1.id,
                     'chronicle_on_accepted': 'chronicle-on-accepted'})

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), data)
        self.bill = prototypes.BillPrototype(models.Bill.objects.all()[0])

        self.request_logout()
        self.request_login(self.account2.email)

        group = utils_permissions.sync_group('bills moderators group', ['bills.moderate_bill'])
        group.user_set.add(self.account2._model)

    def get_post_data(self):
        data = self.bill.user_form_initials
        data.update(linguistics_helpers.get_word_post_data(self.bill.data.name_forms, prefix='name'))
        data['approved'] = True
        return data

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'common.login_required')

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'common.fast_account')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:moderate', args=[666]), self.get_post_data()), 'bills.bill.not_found')

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_ajax_error(self.client.post(django_reverse('game:bills:moderate', args=[self.bill.id])), 'bills.removed')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login(self.account1.email)
        self.check_ajax_error(self.client.post(django_reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'bills.moderator_rights_required')

    def test_wrong_state(self):
        self.bill.state = relations.BILL_STATE.ACCEPTED
        self.bill.save()

        self.check_ajax_error(self.client.post(django_reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()), 'bills.voting_state_required')

    def test_form_errors(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:moderate', args=[self.bill.id]), {}), 'bills.moderate.form_errors')

    def test_moderate_success(self):
        self.account2.prolong_premium(30)
        self.account2.save()

        self.check_ajax_ok(self.client.post(dext_urls.url('game:bills:vote', self.bill.id, type=relations.VOTE_TYPE.FOR.value), {}))

        with self.check_not_changed(forum_models.Post.objects.count):
            with self.check_not_changed(lambda: prototypes.BillPrototype.get_by_id(self.bill.id).updated_at):
                with self.check_not_changed(models.Vote.objects.count):
                    self.check_ajax_ok(self.client.post(django_reverse('game:bills:moderate', args=[self.bill.id]), self.get_post_data()))


class TestDeleteRequests(BaseTestRequests):

    def setUp(self):
        super(TestDeleteRequests, self).setUp()

        new_name = game_names.generator().get_test_name('new-name')

        data = linguistics_helpers.get_word_post_data(new_name, prefix='name')
        data.update({'caption': 'bill-caption',
                     'chronicle_on_accepted': 'chronicle-on-accepted',
                     'place': self.place1.id})

        self.client.post(django_reverse('game:bills:create') + ('?bill_type=%s' % bills.place_renaming.PlaceRenaming.type.value), data)
        self.bill = prototypes.BillPrototype(models.Bill.objects.all()[0])

        self.request_logout()
        self.request_login(self.account2.email)

        group = utils_permissions.sync_group('bills moderators group', ['bills.moderate_bill'])
        group.user_set.add(self.account2._model)

    def test_unlogined(self):
        self.request_logout()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:delete', args=[self.bill.id]), {}), 'common.login_required')

    def test_is_fast(self):
        self.account2.is_fast = True
        self.account2.save()
        self.check_ajax_error(self.client.post(django_reverse('game:bills:delete', args=[self.bill.id]), {}), 'common.fast_account')

    def test_type_not_exist(self):
        self.check_ajax_error(self.client.post(django_reverse('game:bills:delete', args=[666]), {}), 'bills.bill.not_found')

    def test_removed(self):
        self.bill.remove(self.account1)
        self.check_ajax_error(self.client.post(django_reverse('game:bills:delete', args=[self.bill.id])), 'bills.removed')

    def test_no_permissions(self):
        self.request_logout()
        self.request_login(self.accounts_factory.create_account().email)
        self.check_ajax_error(self.client.post(django_reverse('game:bills:delete', args=[self.bill.id]), {}), 'bills.moderator_rights_required')

    def test_delete_success__by_moderator(self):
        self.check_ajax_ok(self.client.post(django_reverse('game:bills:delete', args=[self.bill.id]), {}))

    def test_delete_success__by_owner(self):
        self.request_logout()
        self.request_login(self.account1.email)
        self.check_ajax_ok(self.client.post(django_reverse('game:bills:delete', args=[self.bill.id]), {}))
