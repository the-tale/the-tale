# coding: utf-8

import rels
from rels.django import DjangoEnum

from the_tale.common.postponed_tasks import PostponedLogic, POSTPONED_TASK_LOGIC_RESULT

from the_tale.accounts import prototypes as accounts_prototypes
from the_tale.accounts import logic as accounts_logic

from the_tale.accounts.personal_messages import prototypes


class SendMessagesTask(PostponedLogic):
    TYPE = 'send-messages-task'

    class STATE(DjangoEnum):
        records = ( ('UNPROCESSED', 1, u'в очереди'),
                    ('PROCESSED', 2, u'обработано'),
                    ('BANNED', 3, u'отправитель забанен'),
                    ('SYSTEM_USER', 4, u'нельзя отправлять сообщения системному пользователю'),
                    ('FAST_USER', 5, u'нельзя отправлять сообщения пользователю, не завершившему регистрацию') )


    class STEP(DjangoEnum):
        records = ( ('UNPROCESSED', 1, u'начало обработки'),
                    ('PROCESSED', 2, u'сообщения созданы') )


    def __init__(self, account_id, recipients, message, step=STEP.UNPROCESSED, state=STATE.UNPROCESSED, lot_id=None):
        super(SendMessagesTask, self).__init__()
        self.account_id = account_id
        self.recipients = recipients
        self.message = message
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.step = step if isinstance(step, rels.Record) else self.STEP(step)

    def serialize(self):
        return { 'account_id': self.account_id,
                 'recipients': self.recipients,
                 'message': self.message,
                 'state': self.state.value,
                 'step': self.step.value}

    @property
    def error_message(self): return self.state.text

    def process(self, main_task, storage=None): # pylint: disable=R0911

        if self.step.is_UNPROCESSED:

            account = accounts_prototypes.AccountPrototype.get_by_id(self.account_id)

            system_user = accounts_logic.get_system_user()

            if account.is_ban_forum:
                main_task.comment = 'account is banned'
                self.state = self.STATE.BANNED
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            accounts = accounts_prototypes.AccountPrototype.get_list_by_id(self.recipients)

            for recipient in accounts:

                if recipient.id == system_user.id:
                    main_task.comment = 'system user'
                    self.state = self.STATE.SYSTEM_USER
                    return POSTPONED_TASK_LOGIC_RESULT.ERROR

                if recipient.is_fast:
                    main_task.comment = 'fast user'
                    self.state = self.STATE.FAST_USER
                    return POSTPONED_TASK_LOGIC_RESULT.ERROR

            for recipient in accounts_prototypes.AccountPrototype.get_list_by_id(self.recipients):
                prototypes.MessagePrototype.create(account, recipient, self.message)

            self.step = self.STEP.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
