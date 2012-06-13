# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource
from common.utils.decorators import login_required

from game.heroes.prototypes import get_hero_by_id, ChooseAbilityTaskPrototype
from game.heroes.models import CHOOSE_ABILITY_STATE

class HeroResource(Resource):

    def __init__(self, request, hero_id, *args, **kwargs):
        super(HeroResource, self).__init__(request, *args, **kwargs)

        self.hero_id = int(hero_id)

        if self.account is None or self.account.angel.id != self.hero.angel_id:
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

    @login_required
    @handler('#hero_id', 'choose-ability-dialog', method='get')
    def choose_ability_dialog(self):
        return self.template('heroes/choose_ability.html',
                             {} )

    @login_required
    @handler('#hero_id', 'choose-ability', method='post')
    def choose_ability(self, ability_id):

        from ..workers.environment import workers_environment

        task = ChooseAbilityTaskPrototype.create(ability_id, self.hero.id)

        workers_environment.supervisor.cmd_choose_hero_ability(task.id)

        return self.json(status='processing',
                         status_url=reverse('game:heroes:choose_ability_status', args=[self.hero.id]) + '?task_id=%s' % task.id )

    @login_required
    @handler('#hero_id', 'choose-ability-status', method='get')
    def choose_ability_status(self, task_id):
        ability_task = ChooseAbilityTaskPrototype.get_by_id(task_id)

        if ability_task.hero_id != self.hero.id:
            return self.json(status='error', errors='Вы пытаетесь получить данные о способностях другого героя!')

        if ability_task.state == CHOOSE_ABILITY_STATE.WAITING:
            return self.json(status='processing',
                             status_url=reverse('game:heroes:choose_ability_status', args=[self.hero.id]) + '?task_id=%s' % task_id )
        if ability_task.state == CHOOSE_ABILITY_STATE.PROCESSED:
            return self.json(status='ok')

        return self.json(status='error', error='ошибка при выборе способности')
