
import smart_imports

smart_imports.all()


class UPDATE_ACCOUNT_STATE(rels_django.DjangoEnum):
    records = (('UNPROCESSED', 1, 'необработана'),
               ('PROCESSED', 2, 'обработана'),
               ('WRONG_STATE', 3, 'неверное состояние задачи'))


class UpdateAccount(PostponedLogic):

    TYPE = 'update-account'

    def __init__(self, account_id, method, data, state=UPDATE_ACCOUNT_STATE.UNPROCESSED):
        super(UpdateAccount, self).__init__()
        self.account_id = account_id
        self.method = method.__name__ if isinstance(method, collections.Callable) else method
        self.data = data
        self.state = state if isinstance(state, rels.Record) else UPDATE_ACCOUNT_STATE.index_value[state]

    def serialize(self):
        return {'state': self.state.value,
                'method': self.method,
                'data': self.data,
                'account_id': self.account_id}

    @utils_decorators.lazy_property
    def account(self): return prototypes.AccountPrototype.get_by_id(self.account_id)

    @property
    def error_message(self): return self.state.text

    def process(self, main_task):
        if self.state.is_UNPROCESSED:
            getattr(self.account, self.method)(**self.data)
            self.account.save()
            self.state = UPDATE_ACCOUNT_STATE.PROCESSED
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = UPDATE_ACCOUNT_STATE.WRONG_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR


class TransferMoneyTask(PostponedLogic):
    TYPE = 'transfer-money-task'

    class STATE(rels_django.DjangoEnum):
        records = (('UNPROCESSED', 1, 'в очереди'),
                   ('PROCESSED', 2, 'обработано'),
                   ('TRANSFER_TRANSACTION_REJECTED', 3, 'в переводе отказано'),
                   ('COMMISSION_TRANSACTION_REJECTED', 4, 'невозможно снять комиссию'),
                   ('SENDER_BANNED', 5, 'отправитель забанен'),
                   ('RECIPIENT_BANNED', 6, 'получатель забанен забанен'),
                   ('SENDER_IS_FAST', 7, 'отправитель не завершил регистрацию'),
                   ('RECIPIENT_IS_FAST', 8, 'получатель не завершил регистрацию'),
                   ('TRANSFER_TRANSACTION_WRONG_STATE', 9, 'ошибка при совершении перевода'),
                   ('COMMISSION_TRANSACTION_WRONG_STATE', 10, 'ошибка при начислении комиссии'))

    class STEP(rels_django.DjangoEnum):
        records = (('INITIALIZE', 0, 'инициировать перечисление'),
                   ('WAIT', 1, 'ожидание транзакции'),
                   ('SUCCESS', 2, 'перечисление завершено'),
                   ('ERROR', 3, 'ошибка'))

    def __init__(self, sender_id, recipient_id, amount, commission, comment, transfer_transaction=None, commission_transaction=None, step=None, state=None):

        if step is None:
            step = self.STEP.INITIALIZE

        if state is None:
            state = self.STATE.UNPROCESSED

        super(TransferMoneyTask, self).__init__()

        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.amount = amount
        self.commission = commission
        self.comment = comment
        self.state = state if isinstance(state, rels.Record) else self.STATE(state)
        self.step = step if isinstance(step, rels.Record) else self.STEP(step)
        self.transfer_transaction = bank_transaction.Transaction.deserialize(transfer_transaction) if isinstance(transfer_transaction, dict) else transfer_transaction
        self.commission_transaction = bank_transaction.Transaction.deserialize(commission_transaction) if isinstance(commission_transaction, dict) else commission_transaction

    def serialize(self):
        return {'sender_id': self.sender_id,
                'recipient_id': self.recipient_id,
                'amount': self.amount,
                'commission': self.commission,
                'comment': self.comment,
                'transfer_transaction': self.transfer_transaction.serialize() if self.transfer_transaction else None,
                'commission_transaction': self.commission_transaction.serialize() if self.commission_transaction else None,
                'state': self.state.value,
                'step': self.step.value}

    @property
    def error_message(self): return self.state.text

    @utils_decorators.lazy_property
    def sender(self): return prototypes.AccountPrototype.get_by_id(self.sender_id)

    @utils_decorators.lazy_property
    def recipient(self): return prototypes.AccountPrototype.get_by_id(self.recipient_id)

    def process(self, main_task):

        if self.step.is_INITIALIZE:

            if self.sender.is_fast:
                self.state = self.STATE.SENDER_IS_FAST
                self.step = self.STEP.ERROR
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if self.recipient.is_fast:
                self.state = self.STATE.RECIPIENT_IS_FAST
                self.step = self.STEP.ERROR
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if self.sender.is_ban_any:
                self.state = self.STATE.SENDER_BANNED
                self.step = self.STEP.ERROR
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if self.recipient.is_ban_any:
                self.state = self.STATE.RECIPIENT_BANNED
                self.step = self.STEP.ERROR
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            transfer_invoice = bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                                       recipient_id=self.recipient_id,
                                                                       sender_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                                       sender_id=self.sender_id,
                                                                       currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                                       amount=self.amount,
                                                                       description_for_sender='Перевод игроку «%s»: «%s».' % (self.recipient.nick_verbose, self.comment),
                                                                       description_for_recipient='Перевод от игрока «%s»: «%s».' % (self.sender.nick_verbose, self.comment),
                                                                       operation_uid='transfer-money-between-accounts-transfer')

            self.transfer_transaction = bank_transaction.Transaction(transfer_invoice.id)

            commission_invoice = bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                                         recipient_id=self.sender_id,
                                                                         sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                                         sender_id=0,
                                                                         currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                                         amount=-self.commission,
                                                                         description_for_sender='Комиссия с перевода игроку «%s»: «%s».' % (self.recipient.nick_verbose, self.comment),
                                                                         description_for_recipient='Комиссия с перевода игроку «%s»: «%s».' % (self.recipient.nick_verbose, self.comment),
                                                                         operation_uid=conf.settings.COMMISION_TRANSACTION_UID)

            self.commission_transaction = bank_transaction.Transaction(commission_invoice.id)

            main_task.extend_postsave_actions((lambda: amqp_environment.environment.workers.refrigerator.cmd_wait_task(main_task.id),))

            self.step = self.STEP.WAIT
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE

        if self.step.is_WAIT:

            transfer_transaction_state = self.transfer_transaction.get_invoice_state()
            commission_transaction_state = self.commission_transaction.get_invoice_state()

            if transfer_transaction_state.is_REQUESTED:
                return POSTPONED_TASK_LOGIC_RESULT.WAIT

            if transfer_transaction_state.is_REJECTED:
                self.state = self.STATE.TRANSFER_TRANSACTION_REJECTED
                self.step = self.STEP.ERROR
                main_task.comment = 'invoice %d rejected' % self.transfer_transaction.invoice_id
                self.commission_transaction.cancel()
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if not transfer_transaction_state.is_FROZEN:
                self.state = self.STATE.TRANSFER_TRANSACTION_WRONG_STATE
                self.step = self.STEP.ERROR
                main_task.comment = 'invoice %d rejected' % self.transfer_transaction.invoice_id
                self.commission_transaction.cancel()
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if commission_transaction_state.is_REQUESTED:
                return POSTPONED_TASK_LOGIC_RESULT.WAIT

            if commission_transaction_state.is_REJECTED:
                self.state = self.STATE.COMMISSION_TRANSACTION_REJECTED
                self.step = self.STEP.ERROR
                main_task.comment = 'invoice %d rejected' % self.commission_transaction.invoice_id
                self.transfer_transaction.cancel()
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if not commission_transaction_state.is_FROZEN:
                self.state = self.STATE.COMMISSION_TRANSACTION_WRONG_STATE
                self.step = self.STEP.ERROR
                main_task.comment = 'invoice %d rejected' % self.commission_transaction.invoice_id
                self.transfer_transaction.cancel()
                return POSTPONED_TASK_LOGIC_RESULT.ERROR

            if not (transfer_transaction_state.is_FROZEN and commission_transaction_state.is_FROZEN):
                return POSTPONED_TASK_LOGIC_RESULT.WAIT

            self.transfer_transaction.confirm()
            self.commission_transaction.confirm()

            message = text = 'Игрок «{sender}» перевёл(-а) вам печеньки: {amount} шт. \n\n[quote]{comment}[/quote]'.format(sender=self.sender.nick_verbose,
                                                                                                                           amount=self.amount,
                                                                                                                           comment=self.comment)

            personal_messages_logic.send_message(sender_id=logic.get_system_user_id(),
                                                 recipients_ids=[self.recipient.id],
                                                 body=message,
                                                 asynchronous=True)

            self.state = self.STATE.PROCESSED
            self.step = self.STEP.SUCCESS
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
