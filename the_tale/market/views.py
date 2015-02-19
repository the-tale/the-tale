# coding: utf-8

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url
from dext.common.utils import exceptions as dext_utils_exceptions

from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views
from the_tale.common.utils import pagination

from the_tale.accounts import views as accounts_views


from the_tale.market import relations
from the_tale.market import forms
from the_tale.market import logic
from the_tale.market import models
from the_tale.market import conf

########################################
# processors definition
########################################

class LotProcessor(dext_views.ArgumentProcessor):

    def __init__(self,
                 context_name='lot',
                 error_message=u'Лот не найден',
                 url_name='lot',
                 **kwargs):
        super(LotProcessor, self).__init__(context_name=context_name,
                                           error_message=error_message,
                                           url_name=url_name,
                                           **kwargs)


    def parse(self, context, raw_value):
        try:
            id = int(raw_value)
        except ValueError:
            self.raise_wrong_format(context=context)

        lot = logic.load_lot(id)

        if lot is None:
            self.raise_wrong_value(context=context)

        return lot

# TODO: sync semantics of LotProcessor and LotProcessor.handler
lot_processor = LotProcessor()

class GoodsProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        context.account_goods = logic.load_goods(account_id=context.account.id)

goods_processor = GoodsProcessor()


class GoodProcessor(dext_views.ArgumentProcessor):
    def __init__(self,
                 context_name='good',
                 error_message=u'Неверный идентификатор товара',
                 get_name='good',
                 **kwargs):
        super(GoodProcessor, self).__init__(context_name=context_name,
                                            error_message=error_message,
                                            get_name=get_name,
                                            **kwargs)

    def parse(self, context, raw_value):
        if not context.account_goods.has_good(raw_value):
            self.raise_wrong_value(context)
        return context.account_goods.get_good(raw_value)

good_processor = GoodProcessor()


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='market')
resource.add_processor(accounts_views.account_processor)
resource.add_processor(utils_views.fake_resource_processor)
resource.add_processor(accounts_views.login_required_processor)
resource.add_processor(accounts_views.full_account_processor)
resource.add_processor(accounts_views.ban_game_processor)
resource.add_processor(goods_processor)

########################################
# filters
########################################

class LotsIndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.filter_element(u'поиск:', attribute='filter', default_value=None),
                list_filter.choice_element(u'сортировать:', attribute='order_by', choices=relations.INDEX_ORDER_BY.select('value', 'text'),
                                           default_value=relations.INDEX_ORDER_BY.DATE_DOWN.value),
                list_filter.static_element(u'количество:', attribute='count', default_value=0) ]


########################################
# views
########################################


@dext_views.RelationArgumentProcessor.handler(relation=relations.INDEX_ORDER_BY, default_value=relations.INDEX_ORDER_BY.DATE_DOWN,
                                              error_message=u'неверный тип сортировки',
                                              context_name='order_by', get_name='order_by')
@dext_views.RelationArgumentProcessor.handler(relation=relations.INDEX_MODE, default_value=relations.INDEX_MODE.ALL,
                                              error_message=u'неверный режим отображения',
                                              context_name='page_mode', get_name='page_mode')
@utils_views.text_filter_processor.handler()
@utils_views.page_number_processor.handler()
@resource.handler('')
def index(context):

    lots_query = models.Lot.objects.filter(state=relations.LOT_STATE.ACTIVE)

    if context.page_mode.is_OWN:
        lots_query = lots_query.filter(seller_id=context.account.id)

    if context.filter is not None:
        lots_query = lots_query.filter(name__icontains=context.filter)

    lots_query = lots_query.order_by(context.order_by.db_order)

    lots_count = lots_query.count()

    url_builder = UrlBuilder(url('market:'), arguments={ 'filter': context.filter,
                                                         'order_by': context.order_by.value,
                                                         'page_mode': context.page_mode.value})

    index_filter = LotsIndexFilter(url_builder=url_builder, values={'filter': context.filter,
                                                                    'order_by': context.order_by.value,
                                                                    'count': lots_count,
                                                                    'page_mode': context.page_mode.value})

    paginator = pagination.Paginator(context.page, lots_count, conf.settings.LOTS_ON_PAGE, url_builder)

    if paginator.wrong_page_number:
        return dext_views.Redirect(paginator.last_page_url)

    lots_from, lots_to = paginator.page_borders(context.page)

    lots = logic.load_lots_from_query(lots_query[lots_from:lots_to])

    return dext_views.Page('market/index.html',
                           content={'context': context,
                                    'index_filter': index_filter,
                                    'paginator': paginator,
                                    'lots': lots,
                                    'page_type': 'index' if context.page_mode.is_ALL else 'own-lots',
                                    'resource': context.resource})

@resource.handler('own-lots')
def own_lots(context):
    return dext_views.Redirect(url('market:', page_mode=relations.INDEX_MODE.OWN.value))


@resource.handler('new')
def new(context):
    return dext_views.Page('market/new.html',
                           content={'context': context,
                                    'page_type': 'new',
                                    'resource': context.resource})

@good_processor.handler()
@resource.handler('new-dialog')
def new_dialog(context):
    if logic.has_lot(context.account.id, context.good.uid):
        raise dext_utils_exceptions.ViewError(code='market.new-dialog.lot_exists', message=u'Вы уже выставили этот предмет на продажу')

    return dext_views.Page('market/new_dialog.html',
                           content={'context': context,
                                    'form': forms.PriceForm(initial={'price': conf.settings.MINIMUM_PRICE}),
                                    'resource': context.resource})


@good_processor.handler()
@dext_views.FormProcessor.handler(form_class=forms.PriceForm)
@resource.handler('create', method='POST')
def create(context):
    if logic.has_lot(context.account.id, context.good.uid):
        raise dext_utils_exceptions.ViewError(code='market.create.lot_exists', message=u'Вы уже выставили этот предмет на продажу')

    task = logic.send_good_to_market(seller_id=context.account.id, good=context.good, price=context.form.c.price)
    return dext_views.AjaxProcessing(status_url=task.status_url)


@lot_processor.handler()
@resource.handler('#lot', 'purchase', method='POST')
def purchase(context):

    if not context.lot.state.is_ACTIVE:
        raise dext_utils_exceptions.ViewError(code='market.purchase.wrong_lot_state', message=u'Вы не можете приобрести этот лот')

    if context.lot.seller_id == context.account.id:
        raise dext_utils_exceptions.ViewError(code='market.purchase.can_not_purchase_own_lot', message=u'Нельзя приобрести свой лот')

    if context.account.bank_account.amount < context.lot.price:
        raise dext_utils_exceptions.ViewError(code='market.purchase.no_money', message=u'Не хватает средств для приобретения лота')

    task = logic.purchase_lot(context.account.id, context.lot)
    return dext_views.AjaxProcessing(status_url=task.status_url)
