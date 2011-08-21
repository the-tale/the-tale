# -*- coding: utf-8 -*-

from django_next.views.resources import BaseResource

from game.turns.prototypes import get_latest_turn
from game.angels.prototypes import get_angel_by_model

class Resource(BaseResource):

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(Resource, self).__init__(request, *args, **kwargs)

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = self.user.get_profile()
        return self._account

    @property
    def angel(self):
        if not hasattr(self, '_angel'):
            self._angetl = None
            if self.account:
                self._angel = get_angel_by_model(self.account.angel)
        return self._angel;

    @property
    def turn(self):
        if not hasattr(self, '_turn'):
            self._turn = get_latest_turn()
        return self._turn
            

