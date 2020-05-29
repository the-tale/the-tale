
import smart_imports

smart_imports.all()


def good_bought_message(name, price):
    template = 'Поздравляем! Кто-то купил карту «%(good)s», Вы получаете печеньки: %(price)d шт.'
    return template % {'good': name,
                       'price': price}


class BASE_BUY_TASK_STATE(rels_django.DjangoEnum):
    records = (('TRANSACTION_REQUESTED', 1, 'запрошены средства'),
               ('TRANSACTION_REJECTED', 2, 'недостаточно средств'),
               ('TRANSACTION_FROZEN', 3, 'средства выделены'),
               ('WAIT_TRANSACTION_CONFIRMATION', 4, 'ожидает подтверждение платежа'),
               ('SUCCESSED', 5, 'операция выполнена'),
               ('ERROR_IN_FREEZING_TRANSACTION', 6, 'неверное состояние транзакции при замарозке средств'),
               ('ERROR_IN_CONFIRM_TRANSACTION', 7, 'неверное состояние транзакции при подтверждении траты'),
               ('WRONG_TASK_STATE', 8, 'ошибка при обрабокте задачи — неверное состояние'),
               ('CANCELED', 9, 'операция отменена'), )


class BaseBuyTask(PostponedLogic):
    TYPE = NotImplemented
    RELATION = BASE_BUY_TASK_STATE

    def __init__(self, account_id, transaction, state=None, custom_error=None):
        super(BaseBuyTask, self).__init__()

        if state is None:
            state = self.RELATION.TRANSACTION_REQUESTED

        self.account_id = account_id
        self.state = state if isinstance(state, rels.Record) else self.RELATION.index_value[state]
        self.transaction = bank_transaction.Transaction.deserialize(transaction) if isinstance(transaction, dict) else transaction
        self.custom_error = custom_error

    def __eq__(self, other):
        return (self.state == other.state and
                self.transaction == other.transaction and
                self.account_id == other.account_id and
                self.custom_error == other.custom_error)

    def serialize(self):
        return {'state': self.state.value,
                'transaction': self.transaction.serialize(),
                'account_id': self.account_id,
                'custom_error': self.custom_error}

    @property
    def uuid(self):
        return self.account_id

    @property
    def error_message(self):
        if self.custom_error:
            return self.custom_error
        return self.state.text

    @utils_decorators.lazy_property
    def account(self):
        return accounts_prototypes.AccountPrototype.get_by_id(self.account_id) if self.account_id is not None else None

    def process_transaction_requested(self, main_task):
        transaction_state = self.transaction.get_invoice_state()

        if transaction_state.is_REQUESTED:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        if transaction_state.is_REJECTED:
            self.state = self.RELATION.TRANSACTION_REJECTED
            main_task.comment = 'invoice %d rejected' % self.transaction.invoice_id
            return POSTPONED_TASK_LOGIC_RESULT.ERROR
        elif transaction_state.is_FROZEN:
            self.state = self.RELATION.TRANSACTION_FROZEN
            self.on_process_transaction_requested__transaction_frozen(main_task)
            return POSTPONED_TASK_LOGIC_RESULT.CONTINUE
        else:
            self.state = self.RELATION.ERROR_IN_FREEZING_TRANSACTION
            main_task.comment = 'wrong invoice %d state %r on freezing step' % (self.transaction.invoice_id, transaction_state)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

    def on_process_transaction_requested__transaction_frozen(self, main_task):
        main_task.extend_postsave_actions((main_task.cmd_wait,))

    def on_process_transaction_frozen(self, storage):
        raise NotImplementedError

    def process_transaction_frozen(self, main_task, storage):  # pylint: disable=W0613
        if self.on_process_transaction_frozen(storage=storage):
            self.transaction.confirm()
            self.state = self.RELATION.WAIT_TRANSACTION_CONFIRMATION
            return POSTPONED_TASK_LOGIC_RESULT.WAIT

        else:
            self.transaction.cancel()
            self.state = self.RELATION.CANCELED
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

    def process_transaction_confirmation(self, main_task):
        transaction_state = self.transaction.get_invoice_state()

        if transaction_state.is_FROZEN:
            return POSTPONED_TASK_LOGIC_RESULT.WAIT
        elif transaction_state.is_CONFIRMED:
            self.state = self.RELATION.SUCCESSED
            self.process_referrals()
            return POSTPONED_TASK_LOGIC_RESULT.SUCCESS
        else:
            self.state = self.RELATION.ERROR_IN_CONFIRM_TRANSACTION
            main_task.comment = 'wrong invoice %d state %r on confirmation step' % (self.transaction.invoice_id, transaction_state)
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

    def process(self, main_task, storage=None):  # pylint: disable=W0613

        if self.state.is_TRANSACTION_REQUESTED:
            return self.process_transaction_requested(main_task)

        elif self.state.is_TRANSACTION_FROZEN:
            return self.process_transaction_frozen(main_task, storage=storage)

        elif self.state.is_WAIT_TRANSACTION_CONFIRMATION:
            return self.process_transaction_confirmation(main_task)

        else:
            main_task.comment = 'wrong task state %r' % self.state
            self.state = self.RELATION.WRONG_TASK_STATE
            return POSTPONED_TASK_LOGIC_RESULT.ERROR

    def process_referrals(self):
        invoice = self.transaction.get_invoice()

        if invoice.amount >= 0:
            return

        buyer = accounts_prototypes.AccountPrototype.get_by_id(invoice.recipient_id)

        if buyer.referral_of_id is None:
            return

        owner = accounts_prototypes.AccountPrototype.get_by_id(buyer.referral_of_id)

        logic.transaction_logic(account=owner,
                                amount=-int(invoice.amount * conf.settings.REFERRAL_BONUS),
                                description='Часть от потраченного вашим рефералом',
                                uid='referral-bonus',
                                force=True)


class BuyPremium(BaseBuyTask):
    TYPE = 'purchase-premium'

    def __init__(self, days, **kwargs):
        super(BuyPremium, self).__init__(**kwargs)
        self.days = days

    def __eq__(self, other):
        return (super(BuyPremium, self).__eq__(other) and
                self.days == other.days)

    def serialize(self):
        data = super(BuyPremium, self).serialize()
        data['days'] = self.days
        return data

    def on_process_transaction_frozen(self, **kwargs):
        self.account.prolong_premium(days=self.days)
        self.account.save()

        accounts_logic.update_cards_timer(account=self.account)

        return True


class BuyPermanentPurchase(BaseBuyTask):
    TYPE = 'purchase-permanent-purchase'

    def __init__(self, purchase_type, **kwargs):
        super(BuyPermanentPurchase, self).__init__(**kwargs)
        self.purchase_type = purchase_type if isinstance(purchase_type, rels.Record) else relations.PERMANENT_PURCHASE_TYPE.index_value[purchase_type]

    def __eq__(self, other):
        return (super(BuyPermanentPurchase, self).__eq__(other) and
                self.purchase_type == other.purchase_type)

    def serialize(self):
        data = super(BuyPermanentPurchase, self).serialize()
        data['purchase_type'] = self.purchase_type.value
        return data

    def on_process_transaction_frozen(self, **kwargs):
        self.account.permanent_purchases.insert(self.purchase_type)
        self.account.save()
        return True


class BuyMarketLot(BaseBuyTask):
    TYPE = 'buy-market-lot'

    def __init__(self, item_type, price, **kwargs):
        super(BuyMarketLot, self).__init__(**kwargs)
        self.item_type = item_type
        self.price = price

    def __eq__(self, other):
        return (super(BuyMarketLot, self).__eq__(other) and
                self.item_type == other.item_type and
                self.price == other.price)

    def serialize(self):
        data = super(BuyMarketLot, self).serialize()
        data['item_type'] = self.item_type
        data['price'] = self.price
        return data

    def process_referrals(self):
        pass  # do nothing

    def on_process_transaction_frozen(self, **kwargs):
        lots = tt_services.market.cmd_close_lot(item_type=self.item_type,
                                                price=self.price,
                                                buyer_id=self.account_id)
        if not lots:
            self.custom_error = 'Не удалось купить карту: только что её купил другой игрок.'
            return False

        cards_logic.change_owner(old_owner_id=accounts_logic.get_system_user_id(),
                                 new_owner_id=self.account_id,
                                 operation_type='#close_sell_lots',
                                 new_storage=cards_relations.STORAGE.FAST,
                                 cards_ids=[lot.item_id for lot in lots])

        cards_info = cards_logic.get_cards_info_by_full_types()

        lot = lots[0]

        lot_name = cards_info[lot.full_type]['name']

        # change receiver to lot owner

        invoice = self.transaction.get_invoice()

        invoice._model.recipient_type = bank_relations.ENTITY_TYPE.GAME_ACCOUNT
        invoice._model.recipient_id = lot.owner_id
        invoice._model.save()

        bank_prototypes.InvoicePrototype.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                recipient_id=lot.owner_id,
                                                sender_type=bank_relations.ENTITY_TYPE.GAME_LOGIC,
                                                sender_id=0,
                                                currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                amount=-logic.get_commission(self.price),
                                                description_for_sender='Комиссия с продажи «{}»'.format(lot_name),
                                                description_for_recipient='Комиссия с продажи «{}»'.format(lot_name),
                                                operation_uid='{}-cards-hero-good'.format(conf.settings.MARKET_COMMISSION_OPERATION_UID),
                                                force=True)

        personal_messages_logic.send_message(sender_id=accounts_logic.get_system_user_id(),
                                             recipients_ids=[lot.owner_id],
                                             body=good_bought_message(name=lot_name, price=self.price - logic.get_commission(self.price)),
                                             asynchronous=True)

        return True
