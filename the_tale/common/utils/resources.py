# -*- coding: utf-8 -*-
import time

from dext.views.resources import BaseResource

from accounts.prototypes import AccountPrototype
from accounts.models import Account

from game.prototypes import TimePrototype
from game.conf import game_settings
from game.workers.environment import workers_environment

class Resource(BaseResource):

    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(Resource, self).__init__(request, *args, **kwargs)

        if self.account:
            last_session_refresh_time = request.session.get(game_settings.SESSION_REFRESH_TIME_KEY, None)

            current_timestamp = time.time()

            if last_session_refresh_time is None or last_session_refresh_time + game_settings.SESSION_REFRESH_PERIOD < current_timestamp:
                request.session[game_settings.SESSION_REFRESH_TIME_KEY] = current_timestamp
                workers_environment.supervisor.cmd_mark_hero_as_active(self.account.angel.get_hero().id)


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
