# coding: utf-8

from dext.views import handler, validate_argument

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required

from the_tale.game.heroes.prototypes import HeroPrototype

from the_tale.game.cards import relations
from the_tale.game.cards.prototypes import CARDS


class CardsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(CardsResource, self).initialize(*args, **kwargs)


    @login_required
    @validate_argument('card', lambda v: relations.CARD_TYPE(int(v)), 'cards', u'Неверный идентификатор карты')
    @handler('use-dialog', method='get')
    def use_dialog(self, card):
        hero = HeroPrototype.get_by_account_id(self.account.id)

        if not hero.cards.card_count(card):
            return self.auto_error('cards.no_card', u'У Вас нет такой карты')

        return self.template('cards/use_dialog.html',
                             {'hero': hero,
                              'card': card,
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


        task = CARDS[card]().activate(hero, data={'place_id': int(form.c.place)})

        return self.json_processing(task.status_url)
