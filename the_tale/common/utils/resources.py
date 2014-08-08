# coding: utf-8

from dext.views import BaseResource

from the_tale.amqp_environment import environment

from the_tale.accounts.prototypes import AccountPrototype

from the_tale.game.prototypes import TimePrototype


class Resource(BaseResource):

    ERROR_TEMPLATE = 'error.html'
    DIALOG_ERROR_TEMPLATE = 'dialog_error.html'

    def __init__(self, request, *args, **kwargs):
        super(Resource, self).__init__(request, *args, **kwargs)

        self.account = self.request.user
        if self.account.is_authenticated():
            self.account = AccountPrototype(model=self.account)


    def initialize(self, *args, **kwargs):
        super(Resource, self).initialize(*args, **kwargs)

        if self.account.is_authenticated() and self.account.is_update_active_state_needed:
            environment.workers.accounts_manager.cmd_run_account_method(account_id=self.account.id,
                                                                        method_name=AccountPrototype.update_active_state.__name__,
                                                                        data={})

    @property
    def time(self):
        if not hasattr(self, '_time'):
            self._time = TimePrototype.get_current_time()
        return self._time


    def validate_account_argument(self, account_id):
        if self.account and self.account.id == int(account_id):
            return self.account

        return AccountPrototype.get_by_id(account_id)
