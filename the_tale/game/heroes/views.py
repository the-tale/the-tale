# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from django_next.utils.exceptions import Error

from common.utils.resources import Resource
from common.utils.decorators import login_required

from .prototypes import get_hero_by_id

class HeroResource(Resource):

    def __init__(self, request, hero_id, *args, **kwargs):
        super(HeroResource, self).__init__(request, *args, **kwargs)

        self.hero_id = int(hero_id)

        if self.angel is None or self.angel.id != self.hero.angel_id:
            raise Error(u'Вы не можете просматривать данные этого игрока')


    @property
    def hero(self):
        if not hasattr(self, '_hero'):
            self._hero = get_hero_by_id(self.hero_id)
        return self._hero


    @login_required
    @handler('#hero_id', method='get')
    def hero_page(self):
        return self.template('heroes/hero_page.html',
                             {} )

