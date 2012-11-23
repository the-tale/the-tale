# coding: utf-8
import uuid

from dext.utils.decorators import nested_commit_on_success

from common.utils.enum import create_enum

from common.postponed_tasks import postponed_task

from accounts.prototypes import AccountPrototype

from game.workers.environment import workers_environment as game_workers_environment


REGISTRATION_TASK_STATE = create_enum('REGISTRATION_TASK_STATE', ( ('UNPROCESSED', 0, u'ожидает обработки'),
                                                                   ('PROCESSED', 1, u'обработкана'),
                                                                   ('UNKNOWN_ERROR', 2, u'неизвестная ошибка'),
                                                                   ('BUNDLE_NOT_FOUND', 3, u'аккаунт не создан'),))

@postponed_task
class RegistrationTask(object):

    TYPE = 'registration'

    def __init__(self, account_id, state=REGISTRATION_TASK_STATE.UNPROCESSED):
        self.account_id = account_id
        self.state = state

    def __eq__(self, other):
        return (self.state == other.state and
                self.account_id == other.account_id)

    def serialize(self):
        return { 'state': self.state,
                 'account_id': self.account_id }

    @classmethod
    def deserialize(cls, data):
        return cls(**data)

    @property
    def uuid(self): return 0

    @property
    def response_data(self): return {}

    @property
    def error_message(self): return REGISTRATION_TASK_STATE.CHOICES[self.state]

    @property
    def account(self):
        if not hasattr(self, '_account'):
            self._account = AccountPrototype.get_by_id(self.account_id) if self.account_id is not None else None
        return self._account

    def get_unique_nick(self):
        return uuid.uuid4().hex[:30] # 30 - is django user len limitation

    def unbind_from_account(self):
        self.model.comment = u'unbind from account "%s"' % self.account.nick
        if hasattr(self, '_account'):
            delattr(self, '_account')
        self.model.account = None
        self.model.save()

    def process(self, main_task):
        from accounts.logic import register_user, REGISTER_USER_RESULT
        from game.models import Bundle

        with nested_commit_on_success():

            result, account_id, bundle_id = register_user(nick=self.get_unique_nick())

            if result != REGISTER_USER_RESULT.OK:
                main_task.comment = 'unknown error'
                self.state = REGISTRATION_TASK_STATE.UNKNOWN_ERROR
                return False

        if not Bundle.objects.filter(id=bundle_id).exists():
            main_task.comment = 'bundle %d does not found' % bundle_id
            self.state = REGISTRATION_TASK_STATE.BUNDLE_NOT_FOUND
            return False

        game_workers_environment.supervisor.cmd_register_new_account(account_id)

        self.state = REGISTRATION_TASK_STATE.PROCESSED
        self.account_id = int(account_id)

        return True
