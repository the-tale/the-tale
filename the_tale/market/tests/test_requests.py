# coding: utf-8

from dext.common.utils.urls import url

from the_tale.common.utils import testcase
from the_tale.common.postponed_tasks import models as postponed_tasks_models

from the_tale.accounts import logic as accounts_logic

from the_tale.bank import prototypes as bank_prototypes
from the_tale.bank import relations as bank_relations

from the_tale.game.logic import create_test_map

from the_tale.market import logic
from the_tale.market import models
from the_tale.market import relations
from the_tale.market import goods_types


class RequestsTestsBase(testcase.TestCase):

    def setUp(self):
        super(RequestsTestsBase, self).setUp()

        create_test_map()

        self.account_1 = self.accounts_factory.create_account()
        self.account_2 = self.accounts_factory.create_account()


class IndexRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(IndexRequestsTests, self).setUp()

        self.good_1 = goods_types.test_hero_good.create_good('good-#-1')
        self.good_2 = goods_types.test_hero_good.create_good('good-#-2')
        self.good_3 = goods_types.test_hero_good.create_good('good-#-3')
        self.good_4 = goods_types.test_hero_good.create_good('good-#-4')

        self.price_1 = 1
        self.price_2 = 2
        self.price_3 = 3
        self.price_4 = 4

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.good_1, price=self.price_1)
        self.lot_2 = logic.reserve_lot(self.account_1.id, self.good_2, price=self.price_2)
        self.lot_3 = logic.reserve_lot(self.account_1.id, self.good_3, price=self.price_3)
        self.lot_4 = logic.reserve_lot(self.account_2.id, self.good_4, price=self.price_4)

        self.lot_1.state = relations.LOT_STATE.ACTIVE
        self.lot_2.state = relations.LOT_STATE.ACTIVE
        self.lot_4.state = relations.LOT_STATE.ACTIVE

        logic.save_lot(self.lot_1)
        logic.save_lot(self.lot_2)
        logic.save_lot(self.lot_4)

        self.requested_url = url('market:')


    def test_no_items(self):
        self.request_login(self.account_1.email)
        models.Lot.objects.all().delete()

        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 1),
                                                                         (self.lot_1.name, 0),
                                                                         (self.lot_2.name, 0),
                                                                         (self.lot_3.name, 0),
                                                                         (self.lot_4.name, 0)])

    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 0),
                                                                         self.lot_1.name,
                                                                         self.lot_2.name,
                                                                         (self.lot_3.name, 0),
                                                                         self.lot_4.name])

    def test_normal_view__disabled_records(self):

        self.request_login(self.account_1.email)

        for lot_state in relations.LOT_STATE.records:
            if lot_state.is_ACTIVE:
                continue

            self.lot_2.state = lot_state
            logic.save_lot(self.lot_2)

            self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 0),
                                                                             self.lot_1.name,
                                                                             (self.lot_2.name, 0),
                                                                             (self.lot_3.name, 0),
                                                                             self.lot_4.name])


class OwnLotsRequestsTests(RequestsTestsBase):
    def setUp(self):
        super(OwnLotsRequestsTests, self).setUp()

        self.good_1 = goods_types.test_hero_good.create_good('good-#-1')
        self.good_2 = goods_types.test_hero_good.create_good('good-#-2')
        self.good_3 = goods_types.test_hero_good.create_good('good-#-3')
        self.good_4 = goods_types.test_hero_good.create_good('good-#-4')

        self.price_1 = 1
        self.price_2 = 2
        self.price_3 = 3
        self.price_4 = 4

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.good_1, price=self.price_1)
        self.lot_2 = logic.reserve_lot(self.account_1.id, self.good_2, price=self.price_2)
        self.lot_3 = logic.reserve_lot(self.account_1.id, self.good_3, price=self.price_3)
        self.lot_4 = logic.reserve_lot(self.account_2.id, self.good_4, price=self.price_4)

        self.lot_1.state = relations.LOT_STATE.CLOSED_BY_BUYER
        self.lot_2.state = relations.LOT_STATE.ACTIVE
        self.lot_4.state = relations.LOT_STATE.ACTIVE

        logic.save_lot(self.lot_1)
        logic.save_lot(self.lot_2)
        logic.save_lot(self.lot_4)

        self.requested_url = url('market:own-lots')


    def test_no_items(self):
        self.request_login(self.account_1.email)
        models.Lot.objects.all().delete()

        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 1),
                                                                         (self.lot_1.name, 0),
                                                                         (self.lot_2.name, 0),
                                                                         (self.lot_3.name, 0),
                                                                         (self.lot_4.name, 0)])

    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 0),
                                                                         (self.lot_1.name, 0),
                                                                         self.lot_2.name,
                                                                         (self.lot_3.name, 0),
                                                                         (self.lot_4.name, 0)])

    def test_normal_view__disabled_records(self):

        self.request_login(self.account_1.email)

        for lot_state in relations.LOT_STATE.records:
            if lot_state.is_ACTIVE:
                continue

            self.lot_2.state = lot_state
            logic.save_lot(self.lot_2)

            self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 1),
                                                                             (self.lot_1.name, 0),
                                                                             (self.lot_2.name, 0),
                                                                             (self.lot_3.name, 0),
                                                                             (self.lot_4.name, 0)])




class HistoryRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(HistoryRequestsTests, self).setUp()

        self.good_1 = goods_types.test_hero_good.create_good('good-#-1')
        self.good_2 = goods_types.test_hero_good.create_good('good-#-2')
        self.good_3 = goods_types.test_hero_good.create_good('good-#-3')
        self.good_4 = goods_types.test_hero_good.create_good('good-#-4')

        self.price_1 = 1
        self.price_2 = 2
        self.price_3 = 3
        self.price_4 = 4

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.good_1, price=self.price_1)
        self.lot_2 = logic.reserve_lot(self.account_1.id, self.good_2, price=self.price_2)
        self.lot_3 = logic.reserve_lot(self.account_1.id, self.good_3, price=self.price_3)
        self.lot_4 = logic.reserve_lot(self.account_2.id, self.good_4, price=self.price_4)

        self.lot_1.state = relations.LOT_STATE.CLOSED_BY_BUYER
        self.lot_2.state = relations.LOT_STATE.ACTIVE
        self.lot_4.state = relations.LOT_STATE.CLOSED_BY_BUYER

        logic.save_lot(self.lot_1)
        logic.save_lot(self.lot_2)
        logic.save_lot(self.lot_4)

        self.requested_url = url('market:history')


    def test_no_items(self):
        self.request_login(self.account_1.email)
        models.Lot.objects.all().delete()

        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 1),
                                                                         (self.lot_1.name, 0),
                                                                         (self.lot_2.name, 0),
                                                                         (self.lot_3.name, 0),
                                                                         (self.lot_4.name, 0)])

    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 0),
                                                                         self.lot_1.name,
                                                                         (self.lot_2.name, 0),
                                                                         (self.lot_3.name, 0),
                                                                         self.lot_4.name])

    def test_normal_view__disabled_records(self):

        self.request_login(self.account_1.email)

        for lot_state in relations.LOT_STATE.records:
            if lot_state.is_CLOSED_BY_BUYER:
                continue

            self.lot_1.state = lot_state
            logic.save_lot(self.lot_1)

            self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-lots-message', 0),
                                                                             (self.lot_1.name, 0),
                                                                             (self.lot_2.name, 0),
                                                                             (self.lot_3.name, 0),
                                                                             self.lot_4.name])



class NewRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(NewRequestsTests, self).setUp()

        self.good_1 = goods_types.test_hero_good.create_good('good-1')
        self.good_2 = goods_types.test_hero_good.create_good('good-2')
        self.good_3 = goods_types.test_hero_good.create_good('good-3')
        self.good_4 = goods_types.test_hero_good.create_good('good-4')

        self.goods_1 = logic.load_goods(self.account_1.id)

        self.goods_1.add_good(self.good_1)
        self.goods_1.add_good(self.good_2)
        self.goods_1.add_good(self.good_3)
        self.goods_1.add_good(self.good_4)
        logic.save_goods(self.goods_1)

        self.requested_url = url('market:new')


    def test_no_items(self):
        self.request_login(self.account_1.email)

        self.goods_1.clear()
        logic.save_goods(self.goods_1)

        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-goods-message', 1),
                                                                         (self.good_1.name, 0),
                                                                         (self.good_2.name, 0),
                                                                         (self.good_3.name, 0),
                                                                         (self.good_4.name, 0)])

    def test_anonimouse_view(self):
        self.check_redirect(self.requested_url, accounts_logic.login_page_url(self.requested_url))

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_html(self.requested_url), texts=[('pgf-no-goods-message', 0),
                                                                         self.good_1.name,
                                                                         self.good_2.name,
                                                                         self.good_3.name,
                                                                         self.good_4.name])



class NewDialogRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(NewDialogRequestsTests, self).setUp()

        self.good_1 = goods_types.test_hero_good.create_good('good-1')

        self.goods_1 = logic.load_goods(self.account_1.id)

        self.goods_1.add_good(self.good_1)
        logic.save_goods(self.goods_1)

        self.requested_url = url('market:new-dialog', good=self.good_1.uid)


    def test_no_items(self):
        self.request_login(self.account_1.email)

        self.goods_1.clear()
        logic.save_goods(self.goods_1)

        self.check_html_ok(self.request_ajax_html(self.requested_url), texts=[('market.new-dialog.good.wrong_value', 1)])

    def test_anonimouse_view(self):
        self.check_html_ok(self.request_ajax_html(self.requested_url), texts=[('common.login_required', 1)])

    def test_normal_view(self):
        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url), texts=[self.good_1.name])

    def test_lot_exists(self):
        logic.reserve_lot(self.account_1.id, self.goods_1.get_good(self.good_1.uid), price=777)

        self.request_login(self.account_1.email)
        self.check_html_ok(self.request_ajax_html(self.requested_url), texts=[('market.new-dialog.lot_exists')])



class CreateRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(CreateRequestsTests, self).setUp()

        self.good_1 = goods_types.test_hero_good.create_good('good-1')

        self.goods_1 = logic.load_goods(self.account_1.id)

        self.goods_1.add_good(self.good_1)
        logic.save_goods(self.goods_1)

        self.requested_url = url('market:create', good=self.good_1.uid)

    def test_no_items(self):
        self.request_login(self.account_1.email)

        self.goods_1.clear()
        logic.save_goods(self.goods_1)

        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.requested_url, {'price': 600}), 'market.create.good.wrong_value')

    def test_anonimouse_view(self):
        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.requested_url, {'price': 600}), 'common.login_required')

    def test_low_price(self):
        self.request_login(self.account_1.email)
        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.requested_url, {'price': 0}), 'market.create.form_errors')


    def test_normal_view(self):
        self.request_login(self.account_1.email)

        with self.check_delta(postponed_tasks_models.PostponedTask.objects.count, 1):
            self.check_ajax_processing(self.post_ajax_json(self.requested_url, {'price': 666}))

    def test_lot_exists(self):
        logic.reserve_lot(self.account_1.id, self.goods_1.get_good(self.good_1.uid), price=777)

        self.request_login(self.account_1.email)
        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.requested_url, {'price': 100}), 'market.create.lot_exists')



class PurchaseRequestsTests(RequestsTestsBase):

    def setUp(self):
        super(PurchaseRequestsTests, self).setUp()

        self.good_1 = goods_types.test_hero_good.create_good('good-1')

        self.goods_1 = logic.load_goods(self.account_1.id)

        self.goods_1.add_good(self.good_1)
        logic.save_goods(self.goods_1)

        self.lot_1 = logic.reserve_lot(self.account_1.id, self.goods_1.get_good(self.good_1.uid), price=777)
        self.lot_1.state = relations.LOT_STATE.ACTIVE
        logic.save_lot(self.lot_1)

        self.requested_url = url('market:purchase', self.lot_1.id)


    def test_no_lot(self):
        self.request_login(self.account_2.email)

        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(url('market:purchase', 666)), 'market.purchase.lot.wrong_value')


    def test_anonimouse_view(self):
        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.requested_url), 'common.login_required')


    def test_own_account(self):
        self.request_login(self.account_1.email)
        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.requested_url), 'market.purchase.can_not_purchase_own_lot')


    def test_no_money(self):
        self.request_login(self.account_2.email)
        with self.check_not_changed(postponed_tasks_models.PostponedTask.objects.count):
            self.check_ajax_error(self.post_ajax_json(self.requested_url), 'market.purchase.no_money')


    def test_normal_view(self):
        self.request_login(self.account_2.email)

        bank_account = bank_prototypes.AccountPrototype.create(entity_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                               entity_id=self.account_2.id,
                                                               currency=bank_relations.CURRENCY_TYPE.PREMIUM)
        bank_account.amount = 1000
        bank_account.save()

        with self.check_delta(postponed_tasks_models.PostponedTask.objects.count, 1):
            self.check_ajax_processing(self.post_ajax_json(self.requested_url))
