# coding: utf-8
import datetime

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
from the_tale.market import goods_types

########################################
# processors definition
########################################

class LotProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'lot'
    ERROR_MESSAGE = u'Лот не найден'
    URL_NAME = 'lot'

    def parse(self, context, raw_value):
        try:
            id = int(raw_value)
        except ValueError:
            self.raise_wrong_format()

        lot = logic.load_lot(id)

        if lot is None:
            self.raise_wrong_value()

        return lot


class GoodsProcessor(dext_views.BaseViewProcessor):
    def preprocess(self, context):
        context.account_goods = logic.load_goods(account_id=context.account.id)


class GoodProcessor(dext_views.ArgumentProcessor):
    CONTEXT_NAME = 'good'
    ERROR_MESSAGE = u'Неверный идентификатор товара'
    GET_NAME = 'good'

    def parse(self, context, raw_value):
        if not context.account_goods.has_good(raw_value):
            self.raise_wrong_value()
        return context.account_goods.get_good(raw_value)


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='market')
resource.add_processor(accounts_views.CurrentAccountProcessor())
resource.add_processor(utils_views.FakeResourceProcessor())
resource.add_processor(accounts_views.LoginRequiredProcessor())
resource.add_processor(accounts_views.FullAccountProcessor())
resource.add_processor(accounts_views.BanGameProcessor())
resource.add_processor(GoodsProcessor())

########################################
# filters
########################################

def filter_groups_choices(choice_element):
    choices = [(None, u'все')]

    for group_uid, group in sorted(goods_types.get_groups().iteritems()):
        if 'test' in group_uid:
            continue

        choices.append((group_uid, group.name))

    return choices


class LotsIndexFilter(list_filter.ListFilter):
    ELEMENTS = [list_filter.reset_element(),
                list_filter.filter_element(u'поиск:', attribute='filter', default_value=None),
                list_filter.choice_element(u'сортировать:', attribute='order_by', choices=relations.INDEX_ORDER_BY.select('value', 'text'),
                                           default_value=relations.INDEX_ORDER_BY.DATE_DOWN.value),
                list_filter.choice_element(u'группа:', attribute='group', choices=filter_groups_choices,
                                           default_value=None),
                list_filter.static_element(u'количество:', attribute='count', default_value=0) ]


########################################
# views
########################################

index_resource = dext_views.Resource(name='market')

resource.add_child(index_resource)

index_resource.add_processor(dext_views.RelationArgumentProcessor(relation=relations.INDEX_ORDER_BY, default_value=relations.INDEX_ORDER_BY.DATE_DOWN,
                                                                  error_message=u'неверный тип сортировки',
                                                                  context_name='order_by', get_name='order_by'))
index_resource.add_processor(dext_views.RelationArgumentProcessor(relation=relations.INDEX_MODE, default_value=relations.INDEX_MODE.ALL,
                                                                  error_message=u'неверный режим отображения',
                                                                  context_name='page_mode', get_name='page_mode'))
index_resource.add_processor(dext_views.MapArgumentProcessor(mapping=goods_types.get_groups, default_value=None,
                                                             error_message=u'неверный тип группы', context_name='goods_group', get_name='group'))
index_resource.add_processor(utils_views.TextFilterProcessor())
index_resource.add_processor(utils_views.PageNumberProcessor())


def render_index(context, lots_query, page_mode, base_url):
    if context.filter is not None:
        lots_query = lots_query.filter(name__icontains=context.filter)

    if context.goods_group is not None:
        lots_query = lots_query.filter(type=context.goods_group.type.uid,
                                       group_id=context.goods_group.id)

    lots_query = lots_query.order_by(context.order_by.db_order)

    lots_count = lots_query.count()

    url_builder = UrlBuilder(base_url, arguments={ 'filter': context.filter,
                                                   'order_by': context.order_by.value,
                                                   'group': context.goods_group.uid if context.goods_group else None})

    index_filter = LotsIndexFilter(url_builder=url_builder, values={'filter': context.filter,
                                                                    'order_by': context.order_by.value,
                                                                    'count': lots_count,
                                                                    'group': context.goods_group.uid if context.goods_group else None})

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
                                    'page_type': page_mode.page,
                                    'resource': context.resource})

@index_resource('')
def index(context):
    return render_index(context,
                        models.Lot.objects.filter(state=relations.LOT_STATE.ACTIVE),
                        page_mode=relations.INDEX_MODE.ALL,
                        base_url=url('market:'))

@index_resource('own-lots')
def own_lots(context):
    return render_index(context,
                        models.Lot.objects.filter(seller_id=context.account.id, state=relations.LOT_STATE.ACTIVE),
                        page_mode=relations.INDEX_MODE.OWN,
                        base_url=url('market:own-lots'))

@index_resource('history')
def history(context):
    return render_index(context,
                        models.Lot.objects.filter(state=relations.LOT_STATE.CLOSED_BY_BUYER,
                                                  closed_at__gt=datetime.datetime.now()-datetime.timedelta(days=conf.settings.HISTORY_TIME)),
                        page_mode=relations.INDEX_MODE.HISTORY,
                        base_url=url('market:history'))


@resource('new')
def new(context):
    return dext_views.Page('market/new.html',
                           content={'context': context,
                                    'page_type': 'new',
                                    'resource': context.resource,
                                    'commission': conf.settings.COMMISSION})

@GoodProcessor()
@resource('new-dialog')
def new_dialog(context):
    if logic.has_lot(context.account.id, context.good.uid):
        raise dext_utils_exceptions.ViewError(code='lot_exists', message=u'Вы уже выставили этот предмет на продажу')

    return dext_views.Page('market/new_dialog.html',
                           content={'context': context,
                                    'form': forms.PriceForm(initial={'price': conf.settings.MINIMUM_PRICE}),
                                    'resource': context.resource,
                                    'commission': conf.settings.COMMISSION})


@GoodProcessor()
@dext_views.FormProcessor(form_class=forms.PriceForm)
@resource('create', method='POST')
def create(context):
    if logic.has_lot(context.account.id, context.good.uid):
        raise dext_utils_exceptions.ViewError(code='lot_exists', message=u'Вы уже выставили этот предмет на продажу')

    task = logic.send_good_to_market(seller_id=context.account.id, good=context.good, price=context.form.c.price)
    return dext_views.AjaxProcessing(status_url=task.status_url)


@LotProcessor()
@resource('#lot', 'purchase', method='POST')
def purchase(context):

    if not context.lot.state.is_ACTIVE:
        raise dext_utils_exceptions.ViewError(code='wrong_lot_state', message=u'Вы не можете приобрести этот лот')

    if context.lot.seller_id == context.account.id:
        raise dext_utils_exceptions.ViewError(code='can_not_purchase_own_lot', message=u'Нельзя приобрести свой лот')

    if context.account.bank_account.amount < context.lot.price:
        raise dext_utils_exceptions.ViewError(code='no_money', message=u'Не хватает средств для приобретения лота')

    task = logic.purchase_lot(context.account.id, context.lot)
    return dext_views.AjaxProcessing(status_url=task.status_url)
