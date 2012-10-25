# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from dext.views.resources import handler
from dext.utils.urls import UrlBuilder

from common.utils.resources import Resource
from common.utils.pagination import Paginator

from accounts.prototypes import AccountPrototype
from accounts.models import Account

from game.heroes.prototypes import HeroPrototype
from game.heroes.models import Hero

from game.angels.prototypes import AngelPrototype
from game.angels.conf import angels_settings
from game.angels.models import Angel


class AngelResource(Resource):

    def initialize(self, angel_id=None, *args, **kwargs):
        super(AngelResource, self).initialize(*args, **kwargs)

        if angel_id:
            try:
                self.angel_id = int(angel_id)
            except:
                return self.auto_error('angels.wrong_angel_id', u'Неверный идентификатор игрока', status_code=404)

            if self.angel is None:
                return self.auto_error('angels.angel_not_found', u'Игрок не найден', status_code=404)

    @property
    def angel(self):
        if not hasattr(self, '_angel'):
            self._angel = AngelPrototype.get_by_id(self.angel_id)
        return self._angel

    @handler('', method='get')
    def index(self, page=1):

        angels_count = Angel.objects.filter(account__is_fast=False).count()

        url_builder = UrlBuilder(reverse('game:angels:'), arguments={'page': page})

        page = int(page) - 1

        paginator = Paginator(page, angels_count, angels_settings.ANGELS_ON_PAGE, url_builder)

        if paginator.wrong_page_number:
            return self.redirect(paginator.last_page_url, permanent=False)

        angels_from, angels_to = paginator.page_borders(page)

        angels_models = Angel.objects.filter(account__is_fast=False).select_related().order_by('account__nick')[angels_from:angels_to]

        angels = [AngelPrototype(model) for model in angels_models]

        angels_ids = [ model.id for model in angels_models]

        heroes = dict( (model.angel_id, HeroPrototype(model)) for model in Hero.objects.filter(angel_id__in=angels_ids))

        accounts_ids = [model.account_id for model in angels_models]

        accounts = dict( (model.id, AccountPrototype(model)) for model in Account.objects.select_related().filter(id__in=accounts_ids))

        return self.template('angels/index.html',
                             {'angels': angels,
                              'heroes': heroes,
                              'accounts': accounts,
                              'current_page_number': page,
                              'paginator': paginator  } )

    @handler('#angel_id', name='show', method='get')
    def show(self):
        from forum.models import Thread
        from game.bills.models import Bill

        master_account = self.angel.get_account()

        bills_count = Bill.objects.filter(owner=master_account.model).count()

        threads_count = Thread.objects.filter(author=master_account.model).count()

        threads_with_posts = Thread.objects.filter(post__author=master_account.model).distinct().count()

        return self.template('angels/show.html',
                             {'master_angel': self.angel,
                              'master_hero': self.angel.get_hero(),
                              'master_account': master_account,
                              'bills_count': bills_count,
                              'threads_with_posts': threads_with_posts,
                              'threads_count': threads_count} )
