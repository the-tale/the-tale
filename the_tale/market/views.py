# coding: utf-8

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url
from dext.common.utils import exceptions as dext_utils_exceptions

from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views
from the_tale.common.utils import pagination

from the_tale.accounts import views as accounts_views


from the_tale.market import relations
# from the_tale.market import forms
from the_tale.market import logic
from the_tale.market import models
from the_tale.market import conf

########################################
# processors definition
########################################

class LotProcessor(dext_views.ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            id = int(raw_value)
        except ValueError:
            self.raise_wrong_format(context=context)

        return logic.load_lot(id)

# TODO: sync semantics of LotProcessor and LotProcessor.handler
lot_processor = LotProcessor.handler(error_message=u'лот не найден', url_name='lot', context_name='lot')

class GoodsProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        context.account_goods = logic.load_goods(account_id=context.account.id)

goods_processor = GoodsProcessor.handler()


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
        return context.account_goods.get_good(raw_value)

good_processor = GoodProcessor.handler()

########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='market')
resource.add_processor(accounts_views.account_processor)
resource.add_processor(utils_views.fake_resource_processor)
resource.add_processor(accounts_views.login_required_processor)
resource.add_processor(goods_processor)

########################################
# filters
########################################

class LotsIndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.filter_element(u'поиск:', attribute='filter', default_value=None),
                list_filter.choice_element(u'сортировать:', attribute='order_by', choices=relations.INDEX_ORDER_BY.select('value', 'text'),
                                           default_value=relations.INDEX_ORDER_BY.NAME_UP.value),
                list_filter.static_element(u'количество:', attribute='count', default_value=0) ]


########################################
# views
########################################


@dext_views.RelationArgumentProcessor.handler(relation=relations.INDEX_ORDER_BY, default_value=relations.INDEX_ORDER_BY.NAME_UP,
                                              error_message=u'неверный тип сортировки',
                                              context_name='order_by', get_name='order_by')
@utils_views.text_filter_processor.handler()
@utils_views.page_number_processor.handler()
@resource.handler('')
def index(context):

    lots_query = models.Lot.objects.filter(state=relations.LOT_STATE.ACTIVE)

    if context.filter is not None:
        lots_query = lots_query.filter(name__icontains=context.filter)

    lots_query = lots_query.order_by(context.order_by.db_order)

    lots_count = lots_query.count()

    url_builder = UrlBuilder(url('market:'), arguments={ 'filter': context.filter,
                                                         'order_by': context.order_by.value})

    index_filter = LotsIndexFilter(url_builder=url_builder, values={'filter': context.filter,
                                                                    'order_by': context.order_by.value,
                                                                    'count': lots_count})

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
                                    'resource': context.resource})


@resource.handler('new')
def new(context):
    return dext_views.Page('marker/new.html',
                           content={'context': context,
                                    'resource': context.resource})


@good_processor
@resource.handler('create', method='POST')
def create(context):
    task = logic.send_good_to_market(context.good, cost=context.good_cost)
    return dext_views.AjaxProcessing(status_url=task.status_url)


@lot_processor
@resource.handler('#lot', 'accept', method='POST')
def accept(context):

    if context.lot.seller_id == context.account.id:
        raise dext_utils_exceptions.ViewError(code='market.accept.can_not_accept_own_lot', message=u'Нельзя приобрести свой лот')

    if context.account.bank_account.amount < context.lot.price:
        raise dext_utils_exceptions.ViewError(code='market.accept.no_money', message=u'Не хватает средств для приобретения лота')

    task = logic.purchase_lot(context.lot)
    return dext_views.AjaxProcessing(status_url=task.status_url)
