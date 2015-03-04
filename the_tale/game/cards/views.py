# coding: utf-8

from rels.django import DjangoEnum

from dext.common.utils import views as dext_views
from dext.common.utils.urls import UrlBuilder, url

from the_tale.common.utils import list_filter
from the_tale.common.utils import views as utils_views

from the_tale.accounts import views as accounts_views

from the_tale.game.heroes import views as heroes_views

from the_tale.game.cards import relations
from the_tale.game.cards import effects

########################################
# processors definition
########################################

class AccountCardProcessor(dext_views.ArgumentProcessor):

    def parse(self, context, raw_value):
        try:
            card_uid = int(raw_value)
        except ValueError:
            self.raise_wrong_format(context=context)

        if not context.account_hero.cards.has_card(card_uid=card_uid):
            self.raise_wrong_value(context=context)

        return context.account_hero.cards.get_card(card_uid)


account_card_processor = AccountCardProcessor.handler(error_message=u'У Вас нет такой карты', get_name='card', context_name='account_card')


########################################
# resource and global processors
########################################
resource = dext_views.Resource(name='cards')
resource.add_processor(accounts_views.account_processor)
resource.add_processor(utils_views.fake_resource_processor)
resource.add_processor(heroes_views.account_hero_processor)

guide_resource = dext_views.Resource(name='cards')
guide_resource.add_processor(accounts_views.account_processor)
guide_resource.add_processor(utils_views.fake_resource_processor)

########################################
# filters
########################################

class INDEX_ORDER(DjangoEnum):
    records = ( ('RARITY', 0, u'по редкости'),
                ('NAME', 1, u'по имени') )

CARDS_FILTER = [list_filter.reset_element(),
                list_filter.choice_element(u'редкость:', attribute='rarity', choices=[(None, u'все')] + list(relations.RARITY.select('value', 'text'))),
                list_filter.choice_element(u'доступность:', attribute='availability', choices=[(None, u'все')] + list(relations.AVAILABILITY.select('value', 'text'))),
                list_filter.choice_element(u'сортировка:',
                                           attribute='order_by',
                                           choices=list(INDEX_ORDER.select('value', 'text')),
                                           default_value=INDEX_ORDER.RARITY.value)]

class CardsFilter(list_filter.ListFilter):
    ELEMENTS = CARDS_FILTER



########################################
# views
########################################

@accounts_views.LoginRequiredProcessor.handler()
@account_card_processor
@resource.handler('use-dialog')
def use_dialog(context):
    return dext_views.Page('cards/use_dialog.html',
                           content={'hero': context.account_hero,
                                    'card': context.account_card,
                                    'form': context.account_card.type.form(),
                                    'resource': context.resource} )

@accounts_views.LoginRequiredProcessor.handler()
@account_card_processor
@resource.handler('use', method='POST')
def use(context):
    form = context.account_card.type.form(context.django_request.POST)

    if not form.is_valid():
        raise dext_views.ViewError(code=u'cards.use.form_errors', message=form.errors)

    task = context.account_card.activate(context.account_hero, data=form.get_card_data())

    return dext_views.AjaxProcessing(task.status_url)


@accounts_views.LoginRequiredProcessor.handler()
@resource.handler('combine-dialog')
def combine_dialog(context):
    cards = sorted(effects.EFFECTS.values(), key=lambda x: (x.TYPE.rarity.value, x.TYPE.text))

    return dext_views.Page('cards/combine_dialog.html',
                           content={'CARDS': cards,
                                    'hero': context.account_hero,
                                    'resource': context.resource} )



@dext_views.RelationArgumentProcessor.handler(relation=relations.RARITY, default_value=None,
                                              error_message=u'неверный тип редкости карты',
                                              context_name='cards_rarity', get_name='rarity')
@dext_views.RelationArgumentProcessor.handler(relation=relations.AVAILABILITY, default_value=None,
                                              error_message=u'неверный тип доступности карты',
                                              context_name='cards_availability', get_name='availability')
@dext_views.RelationArgumentProcessor.handler(relation=INDEX_ORDER, default_value=INDEX_ORDER.RARITY,
                                              error_message=u'неверный тип сортировки карт',
                                              context_name='cards_order_by', get_name='order_by')
@guide_resource.handler('')
def index(context):
    from the_tale.game.cards.relations import RARITY

    cards = effects.EFFECTS.values()

    if context.cards_availability:
        cards = [card for card in cards if card.TYPE.availability == context.cards_availability]

    if context.cards_rarity:
        cards = [card for card in cards if card.TYPE.rarity == context.cards_rarity]

    if context.cards_order_by.is_RARITY:
        cards = sorted(cards, key=lambda c: (c.TYPE.rarity.value, c.TYPE.text))
    elif context.cards_order_by.is_NAME:
        cards = sorted(cards, key=lambda c: (c.TYPE.text, c.TYPE.rarity.value))

    url_builder = UrlBuilder(url('guide:cards:'), arguments={ 'rarity': context.cards_rarity.value if context.cards_rarity else None,
                                                              'availability': context.cards_availability.value if context.cards_availability else None,
                                                              'order_by': context.cards_order_by.value})

    index_filter = CardsFilter(url_builder=url_builder, values={'rarity': context.cards_rarity.value if context.cards_rarity else None,
                                                                'availability': context.cards_availability.value if context.cards_availability else None,
                                                                'order_by': context.cards_order_by.value if context.cards_order_by else None})


    return dext_views.Page('cards/index.html',
                           content={'section': 'cards',
                                    'CARDS': cards,
                                    'index_filter': index_filter,
                                    'CARD_RARITY': RARITY,
                                    'resource': context.resource})
