# coding: utf-8

from rels.django import DjangoEnum

from dext.views import handler, validate_argument
from dext.common.utils.urls import UrlBuilder, url

from the_tale.common.utils import list_filter
from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.cards import relations
from the_tale.game.cards import prototypes


class CARDS_ORDER(DjangoEnum):
    records = ( ('RARITY', 0, u'по редкости'),
                ('NAME', 1, u'по имени') )

CARDS_FILTER = [list_filter.reset_element(),
                list_filter.choice_element(u'редкость:', attribute='rarity', choices=[(None, u'все')] + list(relations.RARITY.select('value', 'text'))),
                list_filter.choice_element(u'доступность:', attribute='availability', choices=[(None, u'все')] + list(relations.AVAILABILITY.select('value', 'text'))),
                list_filter.choice_element(u'сортировка:',
                                           attribute='order_by',
                                           choices=list(CARDS_ORDER.select('value', 'text')),
                                           default_value=CARDS_ORDER.RARITY.value)]

class CardsFilter(list_filter.ListFilter):
    ELEMENTS = CARDS_FILTER



class CardsResourceBase(Resource):

    def initialize(self, *args, **kwargs):
        super(CardsResourceBase, self).initialize(*args, **kwargs)


class CardsResource(CardsResourceBase):

    @login_required
    @validate_argument('card', lambda v: relations.CARD_TYPE(int(v)), 'cards', u'Неверный идентификатор карты')
    @handler('use-dialog', method='get')
    def use_dialog(self, card):
        hero = HeroPrototype.get_by_account_id(self.account.id)

        if not hero.cards.card_count(card):
            return self.auto_error('cards.no_card', u'У Вас нет такой карты')

        return self.template('cards/use_dialog.html',
                             {'hero': hero,
                              'card': prototypes.CARDS[card],
                              'form': card.form()} )

    @login_required
    @validate_argument('card', lambda v: relations.CARD_TYPE(int(v)), 'cards', u'Неверный идентификатор карты')
    @handler('use', method='post')
    def use(self, card):
        hero = HeroPrototype.get_by_account_id(self.account.id)

        if not hero.cards.card_count(card):
            return self.auto_error('cards.no_card', u'У Вас нет такой карты')

        form = card.form(self.request.POST)

        if not form.is_valid():
            return self.json_error('cards.use.form_errors', form.errors)

        task = prototypes.CARDS[card].activate(hero, data=form.get_card_data())

        return self.json_processing(task.status_url)

    @login_required
    @handler('combine-dialog', method='get')
    def combine_dialog(self):
        hero = HeroPrototype.get_by_account_id(self.account.id)

        cards = sorted(prototypes.CARDS.values(), key=lambda x: (x.TYPE.rarity.value, x.TYPE.text))

        return self.template('cards/combine_dialog.html',
                             {'CARDS': cards,
                              'hero': hero} )


class GuideCardsResource(CardsResourceBase):

    @validate_argument('rarity', lambda v: relations.RARITY.index_value[int(v)], 'guide.cards', u'неверный тип редкости карты')
    @validate_argument('availability', lambda v: relations.AVAILABILITY.index_value[int(v)], 'guide.cards', u'неверный тип доступности карты')
    @validate_argument('order_by', lambda v: CARDS_ORDER.index_value[int(v)], 'guide.cards', u'неверный тип сортировки карт')
    @handler('', method='get')
    def index(self, rarity=None, availability=None, order_by=CARDS_ORDER.RARITY):
        from the_tale.game.cards.relations import RARITY
        from the_tale.game.cards.prototypes import CARDS

        cards = CARDS.values()

        if availability:
            cards = [card for card in cards if card.TYPE.availability == availability]

        if rarity:
            cards = [card for card in cards if card.TYPE.rarity == rarity]

        if order_by.is_RARITY:
            cards = sorted(cards, key=lambda c: (c.TYPE.rarity.value, c.TYPE.text))
        elif order_by.is_NAME:
            cards = sorted(cards, key=lambda c: (c.TYPE.text, c.TYPE.rarity.value))

        url_builder = UrlBuilder(url('guide:cards:'), arguments={ 'rarity': rarity.value if rarity else None,
                                                                  'availability': availability.value if availability else None,
                                                                  'order_by': order_by.value})

        index_filter = CardsFilter(url_builder=url_builder, values={'rarity': rarity.value if rarity else None,
                                                                    'availability': availability.value if availability else None,
                                                                    'order_by': order_by.value if order_by else None})


        return self.template('cards/index.html', {'section': 'cards',
                                                   'CARDS': cards,
                                                   'index_filter': index_filter,
                                                   'CARD_RARITY': RARITY})
