# coding: utf-8

import datetime

from django.core.urlresolvers import reverse

from dext.views import handler, validator, validate_argument

from the_tale.common.utils.resources import Resource
from the_tale.common.utils.decorators import login_required
from the_tale.common.postponed_tasks import PostponedTaskPrototype

from the_tale.accounts.prototypes import AccountPrototype
from the_tale.accounts.clans.prototypes import ClanPrototype
from the_tale.accounts.payments import price_list

from the_tale.game.balance import constants as c

from the_tale.game.mobs.storage import mobs_storage

from the_tale.game.map.places.storage import places_storage

from the_tale.game.persons.models import PERSON_STATE
from the_tale.game.persons.storage import persons_storage

from the_tale.game.workers.environment import workers_environment

from the_tale.game import names
from the_tale.game.relations import HABIT_TYPE

from the_tale.game.heroes.prototypes import HeroPrototype
from the_tale.game.heroes.postponed_tasks import ChangeHeroTask, ChooseHeroAbilityTask, ChoosePreferencesTask, ResetHeroAbilitiesTask
from the_tale.game.heroes.forms import ChoosePreferencesForm, EditNameForm
from the_tale.game.heroes.conf import heroes_settings

from the_tale.game.cards import relations
from the_tale.game.cards.prototypes import CARDS


class CardsResource(Resource):

    def initialize(self, *args, **kwargs):
        super(CardsResource, self).initialize(*args, **kwargs)


    @login_required
    @handler('deck', method='get')
    def deck(self):
        return self.template('cards/deck.html',
                             {'hero': HeroPrototype.get_by_account_id(self.account.id)} )

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
