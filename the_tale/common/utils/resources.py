# coding: utf-8

from dext.views import BaseResource

from accounts.prototypes import AccountPrototype

from game.prototypes import TimePrototype


class Resource(BaseResource):

    ERROR_TEMPLATE = 'error.html'

    def __init__(self, request, *args, **kwargs):
        super(Resource, self).__init__(request, *args, **kwargs)
        self.account = AccountPrototype(model=self.request.user) if self.request.user.is_authenticated() else self.request.user

    def initialize(self, *args, **kwargs):
        super(Resource, self).initialize(*args, **kwargs)

        if self.account.is_authenticated() and self.account.is_update_active_state_needed:
            from accounts.workers.environment import workers_environment
            workers_environment.accounts_manager.cmd_update_active_state(self.account.id)

    @property
    def time(self):
        if not hasattr(self, '_time'):
            self._time = TimePrototype.get_current_time()
        return self._time


    def validate_account_argument(self, account_id):
        if self.account and self.account.id == int(account_id):
            return self.account

        return AccountPrototype.get_by_id(account_id)
