# -*- coding: utf-8 -*-
import sys
import uuid
import datetime

from dext.utils.decorators import nested_commit_on_success

from accounts.models import Account, RegistrationTask, REGISTRATION_TASK_STATE
from accounts.conf import accounts_settings


def get_account_by_id(model_id):
    angel = Account.objects.get(id=model_id)
    return AccountPrototype(model=angel)

def get_account_by_model(model):
    return AccountPrototype(model=model)

class AccountPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @property
    def id(self): return self.model.id

    @property
    def user(self): return self.model.user

    ###########################################
    # Object operations
    ###########################################

    def remove(self): return self.model.delete()
    def save(self): self.model.save(force_update=True)

    def ui_info(self, ignore_actions=False, ignore_quests=False):
        return {}

    @classmethod
    def create(cls, user):
        account_model = Account.objects.create(user=user)
        return AccountPrototype(model=account_model)


class RegistrationTaskPrototype(object):

    def __init__(self, model=None):
        self.model = model

    @classmethod
    def get_by_id(cls, task_id):
        try:
            model = RegistrationTask.objects.get(id=task_id)
            return cls(model=model)
        except RegistrationTask.DoesNotExist:
            return None
    @classmethod
    def create(cls):
        model = RegistrationTask.objects.create()
        return cls(model=model)

    @property
    def id(self): return self.model.id

    @property
    def state(self): return self.model.state

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = get_account_by_id(self.model.account_id) if self.model.account_id is not None else None
        return self._account

    def get_unique_nick(self):
        return uuid.uuid4().hex

    def process(self, logger):
        from accounts.logic import register_user, REGISTER_USER_RESULT

        from game.workers.environment import workers_environment as game_workers_environment
        from game.models import Bundle

        if self.model.state != REGISTRATION_TASK_STATE.WAITING:
            return

        if self.model.created_at + datetime.timedelta(seconds=accounts_settings.REGISTRATION_TIMEOUT) < datetime.datetime.now():
            self.model.state = REGISTRATION_TASK_STATE.UNPROCESSED
            self.model.comment = 'timeout'
            self.model.save()
            return

        try:
            with nested_commit_on_success():

                result, account_id, bundle_id = register_user(nick=self.get_unique_nick())

                if result == REGISTER_USER_RESULT.OK:
                    pass
                else:
                    self.model.state = REGISTRATION_TASK_STATE.ERROR
                    self.model.comment = 'unknown error'
                    self.model.save()
                    return

            # send command to supervisor after success commit

            if not Bundle.objects.filter(id=bundle_id).exists():
                self.model.state = REGISTRATION_TASK_STATE.ERROR
                self.model.comment = 'bundle %d does not found' % bundle_id
                self.model.save()
                return

            game_workers_environment.supervisor.cmd_register_bundle(bundle_id)

            self.model.state = REGISTRATION_TASK_STATE.PROCESSED
            self.model.comment = 'success'
            self.model.account_id = int(account_id)
            self.model.save()

        except Exception, e:
            logger.error('EXCEPTION: %s' % e)

            exception_info = sys.exc_info()

            logger.error('Worker exception: %r' % self,
                         exc_info=exception_info,
                         extra={} )

            self.model.state = REGISTRATION_TASK_STATE.ERROR
            self.model.comment = u'%s\n\n%s\n\n %s' % exception_info
            self.model.save()
