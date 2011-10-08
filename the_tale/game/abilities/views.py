# coding: utf-8

from django_next.views.resources import handler
from django_next.utils.exceptions import Error

from common.utils.resources import Resource

class AbilitiesResource(Resource):

    def __init__(self, request, ability_type=None, *argv, **kwargs):
        super(AbilitiesResource, self).__init__(request, *argv, **kwargs)
        self.ability_type = ability_type

        if self.ability is None: 
            raise Error(u'У вас нет такой способности')           

        if self.ability.on_cooldown():
            raise Error(u'Способность временно недоступна')

    @property
    def ability(self):
        if self.ability_type in self.angel.abilities:
            return self.angel.abilities[self.ability_type]
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

            if form.c.angel_id != self.angel.id:
                return self.json(status='error', errors='Вы пытаетесь провести операцию для чужого героя, ай-яй-яй, как нехорошо!')        

            data = self.ability.activate(form)
            return self.json(status='ok', data=data)

        return self.json(status='error', errors=form.errors)        


