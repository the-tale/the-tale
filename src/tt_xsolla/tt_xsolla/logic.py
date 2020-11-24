
import asyncio
import aiohttp

from tt_web.results import Ok, Error

from tt_web import log
from tt_web.common import event
from tt_web import postgresql as db

from tt_protocol.protocol import xsolla_pb2

from . import conf
from . import objects
from . import operations


async def find_token(account_info, expiration_delta):
    stored_info = await operations.load_account_info(account_info.id)

    if stored_info is None:
        return Error('AccountInfoNotFound')

    if stored_info.is_removed_by_gdpr():
        return Error('AccountRemovedByGDPR')

    if stored_info.is_changed(account_info):
        return Error('AccountInfoChanged')

    token = await operations.load_token(account_info.id)

    if token is None:
        return Error('TokenNotFound')

    if token.is_expired(expiration_delta):
        return Error('TokenExpired')

    return Ok(token)


async def request_token(account_info, xsolla_client, logger):
    token = await xsolla_client.request_token(account_info, logger)

    if token is None:
        return Error('Token does not received')

    await operations.sync_token_with_account_info(token, account_info)

    return Ok(token)


async def validate_user(account_id):
    stored_info = await operations.load_account_info(account_id)

    if stored_info is None:
        return False

    if stored_info.is_removed_by_gdpr():
        return False

    return stored_info.id == account_id


def invoice_from_xsolla_data(data, is_fake=False):
    return objects.Invoice(xsolla_id=data['transaction']['id'],
                           account_id=int(data['user']['id']),
                           purchased_amount=data['purchase']['virtual_currency']['quantity'],
                           is_test=data['transaction'].get('dry_run') == 1,
                           is_fake=is_fake)


async def register_invoice(invoice):

    stored_account = await operations.load_account_info(invoice.account_id)

    if stored_account is None:
        return Error('NoAccountForInvoice')

    # Do not check "removed by gdpr" state, since info about invoice (amount, game_id, etc) belongs to developers, not to users

    invoice_id = await operations.register_invoice(invoice)

    if invoice_id is not None:
        event.get(conf.PROCESS_INVOICE_EVENT_NAME).set()
        return Ok()

    stored_invoice = await operations.load_invoice(invoice.xsolla_id)

    if stored_invoice is None:
        return Error('UnknownError')

    if invoice == stored_invoice:
        event.get(conf.PROCESS_INVOICE_EVENT_NAME).set()
        return Ok()

    return Error('InvoiceDataDoesNotEqualToStored')


async def register_cancellation(xsolla_id):
    stored_invoice = await operations.load_invoice(xsolla_id)

    if stored_invoice is None:
        return Error('NoInvoiceToCancel')

    cancellation = objects.Cancellation(account_id=stored_invoice.account_id,
                                        xsolla_id=xsolla_id)

    is_registered = await operations.register_cancellation(cancellation)

    if is_registered:
        return Ok()

    stored_cancelation = await operations.load_cancelation(xsolla_id)

    if stored_cancelation is None:
        return Error('UnknownError')

    if cancellation == stored_cancelation:
        return Ok()

    return Error('CancelationDataDoesNotEqualToStored')


async def make_payment(invoice, config, logger):
    async with aiohttp.ClientSession() as session:
        logger.info('try to make payment with url: %s', config['custom']['payment_url'])

        data = xsolla_pb2.PaymentCallbackBody(account_id=invoice.account_id,
                                              amount=invoice.purchased_amount,
                                              secret=config['custom']['secret'])

        async with session.post(config['custom']['payment_url'], data=data.SerializeToString()) as response:
            logger.info('make payment response status: %s', response.status)

            if response.status != 200:
                await asyncio.sleep(config['custom']['sleep_payment_processing_error'])
                return False

            content = await response.read()

            logger.info(content)

            # check if answer in correct format
            xsolla_pb2.PaymentCallbackAnswer.FromString(content)

            return True


async def process_invoice(config, processor, logger):
    logger.info('Try to process invoice')

    try:
        result = await db.transaction(_process_invoice, {'config': config,
                                                         'processor': processor,
                                                         'logger': logger})
    except Exception:
        logger.exception('Error while processing invoice')
        return False

    logger.info('Invoice processed')

    return result


async def _process_invoice(execute, arguments):
    config = arguments['config']
    logger = arguments['logger']
    processor = arguments['processor']

    unprocessed_invoice_id, unprocessed_invoice = await operations.find_and_lock_unprocessed_invoice(execute)

    if unprocessed_invoice is None:
        logger.info('No unprocessed invoices found')
        return False

    logger.info('Unprocessed invoice found, id=%s, xsolla_id=%s', unprocessed_invoice_id, unprocessed_invoice.xsolla_id)

    if unprocessed_invoice.is_test:
        logger.info('It is test invoice, skip processing')
        result = True
    else:
        logger.info('Try to process invoice')
        result = await processor(unprocessed_invoice, config, logger)

    logger.info('Make payment result: %s', result)

    if result:
        await operations.mark_invoice_processed(execute, unprocessed_invoice_id)
        logger.info('Invoice marked as processed')

    return True


async def process_invoices(processor, config):

    logger = log.ContextLogger()

    logger.info('process payments: start')

    requere_processing_event = event.get(conf.PROCESS_INVOICE_EVENT_NAME)

    while True:
        requere_processing_event.clear()

        processor_called = await process_invoice(config, processor, logger)

        if processor_called:
            logger.info('process payments: go to next iteration')
            requere_processing_event.set()
            continue

        logger.info('process_invoice: wait for updates')

        await requere_processing_event.wait()


async def get_data_report(account_id):

    account_info = await operations.load_account_info(account_id)

    if account_info is None:
        return []

    data = []

    data.append(('account_info', account_info.data()))

    for invoice in await operations.load_account_invoices(account_id):
        data.append(('invoice', invoice.data()))

    for cancelation in await operations.load_account_cancelations(account_id):
        data.append(('cancelation', cancelation.data()))

    return data


async def delete_account_data(account_id):

    account_info = await operations.load_account_info(account_id)

    if account_info is None:
        return

    await operations.update_account_info(db.sql, account_info.remove_private_data())
