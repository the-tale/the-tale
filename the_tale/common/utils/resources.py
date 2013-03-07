# -*- coding: utf-8 -*-
import time

from dext.views import BaseResource

from accounts.prototypes import AccountPrototype
from accounts.models import Account

from game.prototypes import TimePrototype
from game.conf import game_settings
from game.workers.environment import workers_environment

from game.heroes.prototypes import HeroPrototype

class Resource(BaseResource):

    ERROR_TEMPLATE = 'error.html'

    def __init__(self, request, *args, **kwargs):
        super(Resource, self).__init__(request, *args, **kwargs)
        self.user = self.request.user


    def initialize(self, *args, **kwargs):
        super(Resource, self).initialize(*args, **kwargs)

        last_session_refresh_time = self.request.session.get(game_settings.SESSION_REFRESH_TIME_KEY, None)

        current_timestamp = time.time()

        if last_session_refresh_time is None or last_session_refresh_time + game_settings.SESSION_REFRESH_PERIOD < current_timestamp:
            self.request.session[game_settings.SESSION_REFRESH_TIME_KEY] = current_timestamp

            if self.account:
                workers_environment.supervisor.cmd_mark_hero_as_active(self.account.id, HeroPrototype.get_by_account_id(self.account.id).id)


    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = None
            try:
                if not self.user.is_anonymous():
                    self._account = AccountPrototype(self.user.get_profile())
            except Account.DoesNotExist:
                pass
        return self._account

    @property
    def time(self):
        if not hasattr(self, '_time'):
            self._time = TimePrototype.get_current_time()
        return self._time


    def validate_account_argument(self, account_id):
        if self.account and self.account.id == int(account_id):
            return self.account

        return AccountPrototype.get_by_id(account_id)
