# -*- coding: utf-8 -*-

from dext.views.resources import BaseResource

from accounts.models import Account

from game.angels.models import Angel
from game.angels.prototypes import get_angel_by_model
from game.prototypes import TimePrototype

class Resource(BaseResource):

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(Resource, self).__init__(request, *args, **kwargs)

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = None
            try:
                if not self.user.is_anonymous():
                    self._account = self.user.get_profile()
            except Account.DoesNotExist:
                pass
        return self._account

    @property
    def angel(self):
        if not hasattr(self, '_angel'):
            self._angel = None
            if self.account is None:
                return self._angel
            try:
                self._angel = get_angel_by_model(self.account.angel)
            except Angel.DoesNotExist:
                pass
        return self._angel

    @property
    def time(self):
        if not hasattr(self, '_time'):
            self._time = TimePrototype.get_current_time()
        return self._time
