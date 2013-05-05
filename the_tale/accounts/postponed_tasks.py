# coding: utf-8
import uuid

import rels
from rels.django_staff import DjangoEnum

from django.core.urlresolvers import reverse

from dext.utils.decorators import nested_commit_on_success

from common.utils.enum import create_enum
from common.utils.decorators import lazy_property

from common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from game.workers.environment import workers_environment as game_workers_environment

from accounts.prototypes import AccountPrototype, ChangeCredentialsTaskPrototype


REGISTRATION_TASK_STATE = create_enum('REGISTRATION_TASK_STATE', ( ('UNPROCESSED', 0, u'ожидает обработки'),
                                                                   ('PROCESSED', 1, u'обработкана'),
                                                                   ('UNKNOWN_ERROR', 2, u'неизвестная ошибка'),
                                                                   ('BUNDLE_NOT_FOUND', 3, u'аккаунт не создан'),))

class RegistrationTask(PostponedLogic):

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

    @property
    def uuid(self): return 0

    @property
    def error_message(self): return REGISTRATION_TASK_STATE._CHOICES[self.state][1]

    @lazy_property
    def account(self): return AccountPrototype.get_by_id(self.account_id) if self.account_id is not None else None

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
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

        if not Bundle.objects.filter(id=bundle_id).exists():
            main_task.comment = 'bundle %d does not found' % bundle_id
            self.state = REGISTRATION_TASK_STATE.BUNDLE_NOT_FOUND
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

        game_workers_environment.supervisor.cmd_register_new_account(account_id)

        self.state = REGISTRATION_TASK_STATE.PROCESSED
        self.account_id = int(account_id)

        return POSTPONED_TASK_LOGIC_RESULT.SUCCESS


class CHANGE_CREDENTIALS_STATE(DjangoEnum):
    _records = ( ('UNPROCESSED', 1, u'необработана'),
                 ('PROCESSED', 2, u'обработана'),
                 ('WRONG_STATE', 3, u'неверное состояние задачи'))


class ChangeCredentials(PostponedLogic):

    TYPE = 'change-credentials'

    def __init__(self, task_id, state=CHANGE_CREDENTIALS_STATE.UNPROCESSED):
        self.task_id = task_id
        self.state = state if isinstance(state, rels.Record) else CHANGE_CREDENTIALS_STATE._index_value[state]

    def __eq__(self, other):
        return (self.state == other.state and
                self.task_id == other.task_id)

    def serialize(self):
        return { 'state': self.state.value,
                 'task_id': self.task_id }

    @property
    def uuid(self): return self.task_id

    @property
    def processed_data(self): return {'next_url': reverse('accounts:profile:edited') }

    def processed_view(self, resource):
        from accounts.logic import force_login_user
        force_login_user(resource.request, self.task.account._model)

        # update account settuped on start of this request processing
        resource.account = self.task.account

    @property
    def error_message(self): return self.state.text

    @lazy_property
    def task(self): return ChangeCredentialsTaskPrototype.get_by_id(self.task_id)

    def process(self, main_task):
        if self.state._is_UNPROCESSED:
            self.task.account.change_credentials(new_email=self.task.new_email,
                                                 new_password=self.task.new_password,
                                                 new_nick=self.task.new_nick)
            self.task.mark_as_processed()
            self.state = CHANGE_CREDENTIALS_STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = CHANGE_CREDENTIALS_STATE.WRONG_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
