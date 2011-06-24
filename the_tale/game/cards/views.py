# -*- coding: utf-8 -*-

from django_next.views.resources import handler
from common.utils.resources import Resource
from common.utils.decorators import login_required

from .models import Card
from .prototypes import get_card_by_id

class CardsResource(Resource):

    def __init__(self, request, card_id=None, *args, **kwargs):
        self.card_id = card_id
        super(CardsResource, self).__init__(request, *args, **kwargs)

    @property
    def card(self):
        if not hasattr(self, '_card'):
            self._card = None
            try:
                self._card = get_card_by_id(self.card_id)
            except Card.DoesNotExist:
                pass
        return self._card

    @handler('#card_id', 'form', method='get')
    @login_required
    def form(self):

        if self.angel.id != self.card.angel_id:
            return self.template('cards/error.html',  {'error': u'this card does not belong to you'} )

        if self.card.cooldown_end > self.turn.number:
            return self.template('cards/error.html',  {'error': u'this card on cooldown'} )

        form = self.card.create_form(self)
        return self.template(self.card.template,
                             {'form': form,
                              'card': self.card} )

    @handler('#card_id', 'activate', method='post')
    @login_required
    def activate(self):

        if self.angel.id != self.card.angel_id:
            return self.json(status='error', error=u'this card does not belong to you' )

        if self.card.cooldown_end > self.turn.number:
            return self.json(status='error', error=u'this card on cooldown')

        if self.card.form:
            form = self.card.create_form(self)

            if form.is_valid():
                self.card.activate(self, form)
                return self.json(status='ok', data={'cooldown_end': self.turn.number+1})
        else:
            self.card.activate(self, form=None)
            return self.json(status='ok', data={'cooldown_end': self.card.cooldown_end})

        return self.json(status='error', errors=form.errors)

