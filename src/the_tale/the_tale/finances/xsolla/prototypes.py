
import smart_imports

smart_imports.all()

BANK_OPERATION_UID = 'bank-xsolla'


class InvoicePrototype(utils_prototypes.BasePrototype):
    _model_class = models.Invoice
    _readonly = ('id',
                 'updated_at',
                 'bank_id',
                 'bank_amount',
                 'bank_invoice_id',
                 'xsolla_id',
                 'xsolla_v1',
                 'xsolla_v2',
                 'xsolla_v3',
                 'test',
                 'date',
                 'comment',
                 'pay_result',
                 'request_url',
                 'created_at')
    _bidirectional = ('state',)
    _get_by = ('id',)

    @classmethod
    def parse_test(cls, test):
        return test not in (None, '0')

    @classmethod
    def get_by_xsolla_id(cls, xsolla_id, test):
        try:
            return cls(model=cls._model_class.objects.get(xsolla_id=xsolla_id, test=test))
        except cls._model_class.DoesNotExist:
            return None

    @classmethod
    def pay(cls, v1, v2, v3, xsolla_id, payment_sum, test, date, request_url):

        invoice = cls.get_by_xsolla_id(xsolla_id=xsolla_id, test=cls.parse_test(test))

        if invoice is not None:
            return invoice

        try:
            return cls.create(v1=v1, v2=v2, v3=v3, xsolla_id=xsolla_id, payment_sum=payment_sum, test=test, date=date, request_url=request_url)
        except django_db.IntegrityError:
            return cls.get_by_xsolla_id(xsolla_id)

    @classmethod
    def create(cls, v1, v2, v3, xsolla_id, payment_sum, test, date, request_url):
        user_email = v1

        results = []

        account_id = bank_logic.get_account_id(email=user_email)

        if account_id is None:
            account_id = -1
            results.append(relations.PAY_RESULT.USER_NOT_EXISTS)

        try:
            real_sum = decimal.Decimal(payment_sum)
        except:
            real_sum = decimal.Decimal('0')
            results.append(relations.PAY_RESULT.WRONG_SUM_FORMAT)

        if real_sum % 1 != 0:
            real_sum //= 1
            results.append(relations.PAY_RESULT.FRACTION_IN_SUM)

        if real_sum <= 0:
            results.append(relations.PAY_RESULT.NOT_POSITIVE_SUM)

        if date is not None:
            try:
                date = datetime.datetime.fromtimestamp(time.mktime(time.strptime(date, '%Y-%m-%d %H:%M:%S')))
            except ValueError:
                date = None
                results.append(relations.PAY_RESULT.WRONG_DATE_FORMAT)

        results.append(relations.PAY_RESULT.SUCCESS)  # success result MUST be appended at the end of every checking

        pay_result = results[0]  # get first result

        model = cls._model_class.objects.create(state=pay_result.invoice_state,
                                                bank_id=account_id,
                                                bank_amount=real_sum,
                                                bank_invoice=None,

                                                xsolla_id=xsolla_id,
                                                xsolla_v1=v1,
                                                xsolla_v2=v2,
                                                xsolla_v3=v3,

                                                pay_result=pay_result,

                                                test=cls.parse_test(test),
                                                date=date,
                                                request_url=request_url[:cls._model_class.REQUEST_URL_LENGTH])

        prototype = cls(model=model)

        if prototype.state.is_CREATED:
            amqp_environment.environment.workers.xsolla_banker.cmd_handle_invoices()

        return prototype

    def process(self):

        if not self.state.is_CREATED:
            raise exceptions.WrongInvoiceStateInProcessingError(invoice_id=self.id, state=self.state)

        if self.test:
            self.state = relations.INVOICE_STATE.SKIPPED_BECOUSE_TEST
            self.save()
            return

        transaction = bank_transaction.Transaction.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                                          recipient_id=self.bank_id,
                                                          sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                                          sender_id=0,
                                                          currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                                          amount=self.bank_amount,
                                                          description_for_sender='Покупка печенек (через Xsolla)',
                                                          description_for_recipient='Покупка печенек (через Xsolla)',
                                                          operation_uid=BANK_OPERATION_UID,
                                                          force=True)

        self._model.bank_invoice_id = transaction.invoice_id
        self.state = relations.INVOICE_STATE.PROCESSED
        self.save()

    @classmethod
    def process_invoices(cls):
        for model in cls._model_class.objects.filter(state=relations.INVOICE_STATE.CREATED).order_by('created_at'):
            invoice = cls(model=model)
            invoice.process()

    def save(self):
        self._model.save()
