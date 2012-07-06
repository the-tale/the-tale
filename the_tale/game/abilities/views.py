# coding: utf-8
from django.core.urlresolvers import reverse

from dext.views.resources import handler
from dext.utils.exceptions import Error

from common.utils.resources import Resource

from .prototypes import AbilityTaskPrototype
from .models import ABILITY_STATE

class AbilitiesResource(Resource):

    def __init__(self, request, ability_type=None, *argv, **kwargs):
        super(AbilitiesResource, self).__init__(request, *argv, **kwargs)
        self.ability_type = ability_type

        if self.account is None:
            raise Error(u'Вы должны представиться')

        if self.ability is None:
            raise Error(u'У вас нет такой способности')

        if self.ability.on_cooldown(self.time, self.account.angel.id):
            raise Error(u'Вы пока не можете использовать эту способность')

    @property
    def ability(self):
        if self.ability_type in self.account.angel.abilities:
            return self.account.angel.abilities[self.ability_type]
        return None

    @handler('#ability_type', 'form', method='get')
    def form(self):

        form = self.ability.create_form(self)

        return self.template(self.ability.TEMPLATE,
                             {'form': form,
                              'ability': self.ability} )

    @handler('#ability_type', 'activate', method='post')
    def activate(self):

        form = self.ability.create_form(self)

        if form.is_valid():

            if form.c.angel_id != self.account.angel.id:
                return self.json(status='error', error='Вы пытаетесь провести операцию для чужого героя, ай-яй-яй, как нехорошо!')

            task = self.ability.activate(form, self.time)

            return self.json(status='processing',
                             status_url=reverse('game:abilities:activate_status', args=[self.ability_type]) + '?task_id=%s' % task.id )

        return self.json(status='error', errors=form.errors)

    @handler('#ability_type', 'activate_status', method='get')
    def activate_status(self, task_id):
        ability_task = AbilityTaskPrototype.get_by_id(task_id)

        if ability_task.type != self.ability_type or ability_task.angel_id != self.account.angel.id:
            return self.json(status='error', errors='Вы пытаетесь получить данные о способностях другого игрока!')

        if ability_task.state == ABILITY_STATE.WAITING:
            return self.json(status='processing', status_url=reverse('game:abilities:activate_status', args=[self.ability_type]) + '?task_id=%s' % task_id )
        if ability_task.state == ABILITY_STATE.PROCESSED:
            return self.json(status='ok', data={'available_at': ability_task.available_at} )

        return self.json(status='error', error='Сейчас нельзя применить эту способность')
