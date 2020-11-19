
import smart_imports
smart_imports.all()


technical_resource = utils_views.Resource(name='bank')


BANK_OPERATION_UID = 'bank-xsolla'


@tt_api_views.RequestProcessor(request_class=tt_protocol_xsolla_pb2.PaymentCallbackBody)
@tt_api_views.SecretProcessor(secret=django_settings.TT_SECRET)
@technical_resource('tt', 'process-payment', name='tt-process-payment', method='post')
@django_decorators.csrf.csrf_exempt
def take_card_callback(context):

    if accounts_prototypes.AccountPrototype.get_by_id(context.tt_request.account_id) is None:
        raise utils_views.ViewError(code='bank.take_card_callback.account_not_found',
                                    message='Account not found')

    bank_transaction.Transaction.create(recipient_type=bank_relations.ENTITY_TYPE.GAME_ACCOUNT,
                                        recipient_id=context.tt_request.account_id,
                                        sender_type=bank_relations.ENTITY_TYPE.XSOLLA,
                                        sender_id=0,
                                        currency=bank_relations.CURRENCY_TYPE.PREMIUM,
                                        amount=context.tt_request.amount,
                                        description_for_sender='Покупка печенек (через Xsolla)',
                                        description_for_recipient='Покупка печенек (через Xsolla)',
                                        operation_uid=BANK_OPERATION_UID,
                                        force=True)

    return tt_api_views.ProtobufOk(content=tt_protocol_xsolla_pb2.PaymentCallbackAnswer())
