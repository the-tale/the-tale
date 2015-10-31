# coding: utf-8

from dext.common.utils.urls import url

from the_tale.common.utils import testcase
from the_tale.common import postponed_tasks as common_postponed_tasks

from the_tale.accounts.logic import register_user
from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.logic import create_test_map
from the_tale.game import names

from the_tale.game.logic_storage import LogicStorage

from the_tale.game.heroes import logic as heroes_logic

from the_tale.game.cards import relations
from the_tale.game.cards.effects import EFFECTS
from the_tale.game.cards import objects
from the_tale.game.cards import logic

from the_tale.game.map.places.prototypes import BuildingPrototype


class CardsRequestsTestsBase(testcase.TestCase):

    def setUp(self):
        super(CardsRequestsTestsBase, self).setUp()
        self.place_1, self.place_2, self.place_3 = create_test_map()

        result, account_id, bundle_id = register_user('test_user_1', 'test_user_1@test.com', '111111')

        self.account = AccountPrototype.get_by_id(account_id)
        self.storage = LogicStorage()
        self.storage.load_account_data(self.account)
        self.hero = self.storage.accounts_to_heroes[self.account.id]

        self.card = objects.Card(relations.CARD_TYPE.KEEPERS_GOODS_COMMON)

        self.building_1 = BuildingPrototype.create(person=self.place_1.persons[0], utg_name=names.generator.get_test_name('building-1-name'))


class UseDialogRequestTests(CardsRequestsTestsBase):

    def test_unlogined(self):
        self.check_html_ok(self.request_ajax_html(url('game:cards:use-dialog', card=666)), texts=['common.login_required'])

    def test_no_cards(self):
        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(url('game:cards:use-dialog', card=666)), texts=['pgf-error-card.wrong_value'])

    def test_has_cards(self):
        self.hero.cards.add_card(self.card)
        heroes_logic.save_hero(self.hero)

        self.request_login(self.account.email)
        self.check_html_ok(self.request_ajax_html(url('game:cards:use-dialog', card=self.card.uid)))



class UseRequestTests(CardsRequestsTestsBase):

    def post_data(self, card_uid, place_id=None, person_id=None, building_id=None):
        return {'place': self.place_1.id if place_id is None else place_id,
                'person': self.place_1.persons[0].id if person_id is None else person_id,
                'building': self.building_1.id if building_id is None else building_id,}

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(666), self.post_data(666)), 'common.login_required')

    def test_no_cards(self):
        self.request_login(self.account.email)
        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(666)), 'card.wrong_value')


    def test_form_invalid(self):
        self.request_login(self.account.email)

        self.hero.cards.add_card(self.card)
        heroes_logic.save_hero(self.hero)

        self.check_ajax_error(self.post_ajax_json(logic.use_card_url(self.card.uid),
                                                  self.post_data(self.card.uid, place_id=666, building_id=666, person_id=666)), 'form_errors')


    def test_success(self):
        self.request_login(self.account.email)

        self.hero.cards.add_card(self.card)
        heroes_logic.save_hero(self.hero)

        response = self.post_ajax_json(logic.use_card_url(self.card.uid), self.post_data(self.card.uid))
        task = common_postponed_tasks.PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)

        task.remove()


class TestIndexRequests(CardsRequestsTestsBase):

    def setUp(self):
        super(TestIndexRequests, self).setUp()

    def test_simple(self):
        texts = [card.TYPE.text for card in EFFECTS.values()]
        self.check_html_ok(self.request_html(url('guide:cards:')), texts=texts)

    def test_rarity_filter(self):
        for rarity in relations.RARITY.records:
            texts = [card.TYPE.text for card in EFFECTS.values() if card.TYPE.rarity == rarity]
            self.check_html_ok(self.request_html(url('guide:cards:')), texts=texts)

    def test_availability_filter(self):
        for availability in relations.AVAILABILITY.records:
            texts = [card.TYPE.text for card in EFFECTS.values() if card.TYPE.availability == availability]
            self.check_html_ok(self.request_html(url('guide:cards:')), texts=texts)


class GetCardRequestsTests(CardsRequestsTestsBase):

    def setUp(self):
        super(GetCardRequestsTests, self).setUp()

    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.get_card_url()), 'common.login_required')

    def test_created(self):
        self.request_login(self.account.email)

        with self.check_delta(common_postponed_tasks.PostponedTaskPrototype._db_count, 1):
            response = self.post_ajax_json(logic.get_card_url())

        task = common_postponed_tasks.PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)


class CombineCardsRequestsTests(CardsRequestsTestsBase):

    def setUp(self):
        super(CombineCardsRequestsTests, self).setUp()


    def test_unlogined(self):
        self.check_ajax_error(self.post_ajax_json(logic.combine_cards_url(())), 'common.login_required')


    def test_created(self):
        self.request_login(self.account.email)

        card_1 = objects.Card(relations.CARD_TYPE.ADD_GOLD_COMMON)
        card_2 = objects.Card(relations.CARD_TYPE.ADD_GOLD_COMMON)

        self.hero.cards.add_card(card_1)
        self.hero.cards.add_card(card_2)

        heroes_logic.save_hero(self.hero)

        with self.check_delta(common_postponed_tasks.PostponedTaskPrototype._db_count, 1):
            response = self.post_ajax_json(logic.combine_cards_url((card_1.uid, card_2.uid) ))

        task = common_postponed_tasks.PostponedTaskPrototype._db_get_object(0)

        self.check_ajax_processing(response, task.status_url)


    def test_wrong_cards(self):
        self.request_login(self.account.email)

        for combine_status in relations.CARDS_COMBINING_STATUS.records:
            if combine_status.is_ALLOWED:
                continue

            with self.check_not_changed(common_postponed_tasks.PostponedTaskPrototype._db_count):
                self.check_ajax_error(self.post_ajax_json(logic.combine_cards_url((666,))),
                                      'cards.wrong_value')
