# -*- coding: utf-8 -*-

from django_next.views.resources import BaseResource

from game.angels.prototypes import get_angel_by_model
from game.prototypes import get_current_time

class Resource(BaseResource):

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(Resource, self).__init__(request, *args, **kwargs)

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = None if self.user.is_anonymous() else self.user.get_profile()
        return self._account

    @property
    def angel(self):
        if not hasattr(self, '_angel'):
            self._angel = None
            if self.account:
                self._angel = get_angel_by_model(self.account.angel)
        return self._angel            

    @property
    def time(self):
        if not hasattr(self, '_time'):
            self._time = get_current_time()
        return self._time

